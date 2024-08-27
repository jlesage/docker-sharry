#!/bin/sh

set -e # Exit immediately if a command exits with a non-zero status.
set -u # Treat unset variables as an error.

# Unset any SHARRY_* variables set to value "UNSET". Useful to ignore a
# configuration option defined with a default environment variable: this allows
# the use of the value from the configuration file instead.
for VAR in $(env | grep "^SHARRY_" | grep "=UNSET$" | cut -d'=' -f1)
do
    is-bool-val-false "${CONTAINER_DEBUG:-0}" || echo "ignoring environment variable: $VAR"
    unset "$VAR"
done

exec /opt/sharry/bin/sharry-restserver /config/sharry.conf

# vim:ft=sh:ts=4:sw=4:et:sts=4
