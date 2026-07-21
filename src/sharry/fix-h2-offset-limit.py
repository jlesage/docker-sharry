#!/usr/bin/env python3
"""
Patch Sharry's backend JAR to fix share listing on H2/MariaDB.

Upstream bug: https://github.com/eikek/sharry/issues/1643
Fix:         https://github.com/eikek/sharry/pull/1776

The compiled query uses doobie fragments equivalent to:
  ORDER BY ... DESC OFFSET ? LIMIT ?
H2 and MariaDB require:
  ORDER BY ... DESC LIMIT ? OFFSET ?

Changing only the SQL text is not enough: the bound parameters must also
be reordered (limit first, then offset). Otherwise H2 silently runs
  LIMIT <offset> OFFSET <limit>
which for the default first page is LIMIT 0 OFFSET 100 — empty list, no error.

This rewrites string parts in Queries$.class and swaps Page.offset /
Page.limit invokes in findShares so SQL and parameters stay consistent.
"""

from __future__ import annotations

import struct
import sys
import zipfile
from pathlib import Path

CLASS_NAME = "sharry/backend/share/Queries$.class"

# CONSTANT_Utf8 entries as they appear in the 1.15+/1.16 broken builds.
UTF8_BROKEN_OFFSET = b"\x01\x00\x07OFFSET "
UTF8_BROKEN_LIMIT = b"\x01\x00\x07 LIMIT "

# Fixed forms (PR #1776 / post-1.16.0 master), same total length as broken pair.
UTF8_FIXED_LIMIT = b"\x01\x00\x06LIMIT "
UTF8_FIXED_OFFSET = b"\x01\x00\x08 OFFSET "


def _parse_constant_pool(data: bytes):
    """Return (cp_list, pos_after_cp). cp_list is 1-indexed; Long/Double leave a hole."""
    pos = 8
    cp_count = struct.unpack(">H", data[pos : pos + 2])[0]
    pos += 2
    cp = [None]
    i = 1
    while i < cp_count:
        tag = data[pos]
        entry = {"tag": tag, "pos": pos}
        if tag == 1:  # Utf8
            length = struct.unpack(">H", data[pos + 1 : pos + 3])[0]
            entry["s"] = data[pos + 3 : pos + 3 + length]
            pos += 3 + length
        elif tag in (7, 8, 16, 19, 20):
            entry["ref"] = struct.unpack(">H", data[pos + 1 : pos + 3])[0]
            pos += 3
        elif tag in (3, 4):
            pos += 5
        elif tag in (9, 10, 11, 12, 17, 18):
            entry["a"], entry["b"] = struct.unpack(">HH", data[pos + 1 : pos + 5])
            pos += 5
        elif tag in (5, 6):
            pos += 9
            cp.append(entry)
            cp.append(None)
            i += 2
            continue
        elif tag == 15:
            pos += 4
        else:
            raise RuntimeError(f"unsupported constant pool tag {tag} at {pos}")
        cp.append(entry)
        i += 1
    return cp, pos


def _utf8(cp, index: int) -> str:
    entry = cp[index]
    if entry is None or entry["tag"] != 1:
        raise RuntimeError(f"constant #{index} is not Utf8")
    return entry["s"].decode("utf-8")


def _find_methodref(cp, class_suffix: str, method: str, descriptor: str) -> int:
    for i, entry in enumerate(cp):
        if entry is None or entry["tag"] not in (10, 11):  # Methodref / InterfaceMethodref
            continue
        cls = cp[entry["a"]]
        nat = cp[entry["b"]]
        if cls is None or cls["tag"] != 7 or nat is None or nat["tag"] != 12:
            continue
        cname = _utf8(cp, cls["ref"])
        mname = _utf8(cp, nat["a"])
        mdesc = _utf8(cp, nat["b"])
        if cname.endswith(class_suffix) and mname == method and mdesc == descriptor:
            return i
    raise RuntimeError(f"methodref not found: {class_suffix}.{method}{descriptor}")


def _find_string_indices_for_payload(cp, payload: bytes) -> list[int]:
    """All CONSTANT_String indices whose Utf8 payload equals payload."""
    utf8_indices = [
        i
        for i, entry in enumerate(cp)
        if entry is not None and entry["tag"] == 1 and entry["s"] == payload
    ]
    if not utf8_indices:
        return []
    utf8_set = set(utf8_indices)
    return [
        i
        for i, entry in enumerate(cp)
        if entry is not None and entry["tag"] == 8 and entry["ref"] in utf8_set
    ]


def _replace_utf8(data: bytearray, old_entry: bytes, new_str: bytes) -> None:
    pos = data.find(old_entry)
    if pos < 0:
        raise RuntimeError(f"UTF8 entry not found: {old_entry!r}")
    if data.find(old_entry, pos + 1) >= 0:
        raise RuntimeError(f"UTF8 entry not unique: {old_entry!r}")
    new_entry = b"\x01" + struct.pack(">H", len(new_str)) + new_str
    data[pos : pos + len(old_entry)] = new_entry


def _ldc_w(index: int) -> bytes:
    return bytes([0x13]) + struct.pack(">H", index)


def _invokevirtual(index: int) -> bytes:
    return bytes([0xB6]) + struct.pack(">H", index)


def _find_paging_marker(data: bytes, part0_str: int, part1_str: int) -> int:
    """
    Locate the findShares StringContext that builds the paging clause.

    Pattern (astore into Object[3]):
      dup; iconst_0; ldc_w #part0; aastore
      dup; iconst_1; ldc_w #part1; aastore
      dup; iconst_2; ldc_w #empty; aastore

    The empty-string constant index is discovered by scanning candidates.
    """
    head = (
        bytes([0x59, 0x03])
        + _ldc_w(part0_str)
        + bytes([0x53])
        + bytes([0x59, 0x04])
        + _ldc_w(part1_str)
        + bytes([0x53])
        + bytes([0x59, 0x05])
    )
    # After head: ldc_w #empty; aastore  =>  13 XX XX 53
    positions = []
    start = 0
    while True:
        pos = data.find(head, start)
        if pos < 0:
            break
        tail = data[pos + len(head) : pos + len(head) + 4]
        if len(tail) == 4 and tail[0] == 0x13 and tail[3] == 0x53:
            positions.append(pos)
        start = pos + 1
    if not positions:
        raise RuntimeError("could not locate findShares paging StringContext bytecode")
    if len(positions) > 1:
        raise RuntimeError(f"paging StringContext marker not unique ({len(positions)} hits)")
    return positions[0]


def _find_page_invokes(
    data: bytes, marker_pos: int, mr_offset: int, mr_limit: int
) -> tuple[int, int]:
    """Return absolute file offsets of Page.offset / Page.limit invokes after marker."""
    inv_offset = _invokevirtual(mr_offset)
    inv_limit = _invokevirtual(mr_limit)
    window = data[marker_pos : marker_pos + 256]
    rel_off = window.find(inv_offset)
    rel_lim = window.find(inv_limit)
    if rel_off < 0 or rel_lim < 0:
        raise RuntimeError("Page.offset/limit invokes not found near paging marker")
    # Ensure these are the pair used for the interpolator args (exactly one each in window).
    if window.find(inv_offset, rel_off + 1) >= 0 or window.find(inv_limit, rel_lim + 1) >= 0:
        raise RuntimeError("ambiguous Page.offset/limit invokes near paging marker")
    return marker_pos + rel_off, marker_pos + rel_lim


def _strings_are_fixed(data: bytes) -> bool:
    return (
        UTF8_FIXED_LIMIT in data
        and UTF8_FIXED_OFFSET in data
        and UTF8_BROKEN_OFFSET not in data
        and UTF8_BROKEN_LIMIT not in data
    )


def _strings_are_broken(data: bytes) -> bool:
    return data.count(UTF8_BROKEN_OFFSET) == 1 and data.count(UTF8_BROKEN_LIMIT) == 1


def patch_class(data: bytearray) -> str:
    """
    Patch Queries$.class in-place.

    Returns a short status: 'patched', 'repaired-binds', or 'already-fixed'.
    """
    cp, _ = _parse_constant_pool(bytes(data))
    mr_offset = _find_methodref(cp, "sharry/common/Page", "offset", "()I")
    mr_limit = _find_methodref(cp, "sharry/common/Page", "limit", "()I")

    actions: list[str] = []

    # --- 1) SQL clause text -------------------------------------------------
    if _strings_are_broken(data):
        # Resolve String CP indices while payloads are still the broken forms.
        part0_candidates = _find_string_indices_for_payload(cp, b"OFFSET ")
        part1_candidates = _find_string_indices_for_payload(cp, b" LIMIT ")
        if len(part0_candidates) != 1 or len(part1_candidates) != 1:
            raise RuntimeError(
                f"unexpected String constants for OFFSET/LIMIT "
                f"(offset={part0_candidates}, limit={part1_candidates})"
            )
        part0_str = part0_candidates[0]
        part1_str = part1_candidates[0]

        # Replace later pool entry first so earlier offsets stay valid while
        # lengths change. Net size change is 0.
        if data.find(UTF8_BROKEN_LIMIT) < data.find(UTF8_BROKEN_OFFSET):
            raise RuntimeError("unexpected constant pool order for OFFSET/LIMIT strings")
        _replace_utf8(data, UTF8_BROKEN_LIMIT, b" OFFSET ")
        _replace_utf8(data, UTF8_BROKEN_OFFSET, b"LIMIT ")
        actions.append("strings")
    elif _strings_are_fixed(data):
        part0_candidates = _find_string_indices_for_payload(cp, b"LIMIT ")
        part1_candidates = _find_string_indices_for_payload(cp, b" OFFSET ")
        if len(part0_candidates) != 1 or len(part1_candidates) != 1:
            raise RuntimeError(
                f"unexpected fixed String constants "
                f"(limit={part0_candidates}, offset={part1_candidates})"
            )
        part0_str = part0_candidates[0]
        part1_str = part1_candidates[0]
    else:
        raise RuntimeError(
            "unexpected OFFSET/LIMIT UTF8 constants "
            f"(broken_offset={data.count(UTF8_BROKEN_OFFSET)}, "
            f"broken_limit={data.count(UTF8_BROKEN_LIMIT)}, "
            f"fixed_limit={data.count(UTF8_FIXED_LIMIT)}, "
            f"fixed_offset={data.count(UTF8_FIXED_OFFSET)}); refusing to patch"
        )

    # --- 2) Bind parameter order -------------------------------------------
    # After the string rewrite, part0 is LIMIT and part1 is OFFSET. The args
    # must therefore be limit then offset.
    marker_pos = _find_paging_marker(bytes(data), part0_str, part1_str)
    off_pos, lim_pos = _find_page_invokes(bytes(data), marker_pos, mr_offset, mr_limit)

    # Desired order: limit invoke first, offset invoke second.
    if lim_pos < off_pos:
        # Already limit-then-offset.
        pass
    elif off_pos < lim_pos:
        data[off_pos : off_pos + 3] = _invokevirtual(mr_limit)
        data[lim_pos : lim_pos + 3] = _invokevirtual(mr_offset)
        actions.append("binds")
    else:
        raise RuntimeError("offset/limit invoke positions are identical")

    # --- 3) Verify final state ---------------------------------------------
    if not _strings_are_fixed(data):
        raise RuntimeError("post-condition failed: SQL strings not fixed")
    off_pos2, lim_pos2 = _find_page_invokes(bytes(data), marker_pos, mr_offset, mr_limit)
    if not (lim_pos2 < off_pos2):
        raise RuntimeError(
            "post-condition failed: Page.limit must be bound before Page.offset "
            f"(limit@{lim_pos2}, offset@{off_pos2})"
        )

    if not actions:
        return "already-fixed"
    if actions == ["binds"]:
        return "repaired-binds"
    return "patched"


def patch_jar(jar_path: Path) -> str:
    jar_path = jar_path.resolve()
    if not jar_path.is_file():
        raise RuntimeError(f"JAR not found: {jar_path}")

    with zipfile.ZipFile(jar_path, "r") as zin:
        names = zin.namelist()
        if CLASS_NAME not in names:
            raise RuntimeError(f"{CLASS_NAME} not found in {jar_path.name}")
        class_data = bytearray(zin.read(CLASS_NAME))
        status = patch_class(class_data)

        if status == "already-fixed":
            return status

        tmp_path = jar_path.with_suffix(jar_path.suffix + ".tmp")
        with zipfile.ZipFile(tmp_path, "w") as zout:
            for item in zin.infolist():
                content = zin.read(item.filename)
                if item.filename == CLASS_NAME:
                    content = bytes(class_data)
                info = zipfile.ZipInfo(filename=item.filename, date_time=item.date_time)
                info.compress_type = item.compress_type
                info.external_attr = item.external_attr
                zout.writestr(info, content)

    tmp_path.replace(jar_path)
    return status


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <sharry-backend-*.jar>", file=sys.stderr)
        return 2
    jar = Path(argv[1])
    try:
        status = patch_jar(jar)
    except Exception as exc:  # noqa: BLE001 - surface build failure clearly
        print(f"ERROR: failed to patch {jar}: {exc}", file=sys.stderr)
        return 1
    print(f"{jar.name}: {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
