#!/usr/bin/env bash
# Bootstraps a per-user Postgres instance on a shared cluster (e.g. CHPC) where
# you have `module load postgresql` but no system-wide server running and no
# root access. Safe to re-run (idempotent): it will reuse an existing data dir
# and just (re)start the server if needed.
#
# Usage:
#   module load postgresql
#   source setup_local_postgres.sh
#
# After sourcing, SQLMORPHER_PG_* env vars are set in your shell and
# run_auto_pipeline.py will pick them up automatically.

set -euo pipefail

PGDATA_DIR="${SQLMORPHER_PGDATA:-$HOME/.sqlmorpher/pgdata}"
PGPORT="${SQLMORPHER_PG_PORT:-5433}"
PGUSER="${SQLMORPHER_PG_USER:-$USER}"
PGDBNAME="${SQLMORPHER_PG_DBNAME:-sqlmorpher}"
PGLOG="${SQLMORPHER_PGLOG:-$HOME/.sqlmorpher/pg.log}"

mkdir -p "$(dirname "$PGDATA_DIR")" "$(dirname "$PGLOG")"

if ! command -v initdb >/dev/null 2>&1; then
    echo "ERROR: 'initdb' not found. Did you run 'module load postgresql'?" >&2
    return 1 2>/dev/null || exit 1
fi

if [ ! -d "$PGDATA_DIR" ] || [ ! -f "$PGDATA_DIR/PG_VERSION" ]; then
    echo "Initializing new Postgres data directory at $PGDATA_DIR ..."
    initdb -D "$PGDATA_DIR" -U "$PGUSER" --auth=trust
    # Listen only on localhost/loopback (no external exposure needed on a
    # shared cluster) and use a non-default port to avoid clashing with
    # other users' instances.
    sed -i.bak "s/^#port = 5432/port = ${PGPORT}/" "$PGDATA_DIR/postgresql.conf" || true
    echo "port = ${PGPORT}" >> "$PGDATA_DIR/postgresql.conf"
    echo "listen_addresses = 'localhost'" >> "$PGDATA_DIR/postgresql.conf"
fi

if pg_ctl -D "$PGDATA_DIR" status >/dev/null 2>&1; then
    echo "Postgres is already running for $PGDATA_DIR."
else
    echo "Starting Postgres on port $PGPORT ..."
    pg_ctl -D "$PGDATA_DIR" -l "$PGLOG" -o "-p ${PGPORT}" start
    sleep 2
fi

# Create the working database if it doesn't exist yet.
if ! psql -h localhost -p "$PGPORT" -U "$PGUSER" -d postgres -tAc \
        "SELECT 1 FROM pg_database WHERE datname='${PGDBNAME}'" | grep -q 1; then
    echo "Creating database '${PGDBNAME}' ..."
    createdb -h localhost -p "$PGPORT" -U "$PGUSER" "$PGDBNAME"
fi

export SQLMORPHER_PG_HOST="localhost"
export SQLMORPHER_PG_PORT="$PGPORT"
export SQLMORPHER_PG_USER="$PGUSER"
export SQLMORPHER_PG_DBNAME="$PGDBNAME"
export SQLMORPHER_PG_PASSWORD=""

echo ""
echo "Postgres ready:"
echo "  host=localhost port=${PGPORT} user=${PGUSER} dbname=${PGDBNAME}"
echo "  data dir: ${PGDATA_DIR}"
echo "  log file: ${PGLOG}"
echo ""
echo "Env vars exported in this shell. Run SQLMorpher from here, e.g.:"
echo "  python run_auto_pipeline.py --cases 1_20 --model qwen2.5-coder:32b"
echo ""
echo "To stop the server later: pg_ctl -D ${PGDATA_DIR} stop"
