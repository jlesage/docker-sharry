#!/bin/sh

set -e # Exit immediately if a command exits with a non-zero status.
set -u # Treat unset variables as an error.

exec /opt/sharry/bin/sharry-restserver /config/sharry.conf

# vim:ft=sh:ts=4:sw=4:et:sts=4
