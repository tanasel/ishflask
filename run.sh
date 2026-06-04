#!/bin/sh
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
DIR=$(cd "$(dirname "$0")" && pwd)
. "$DIR/bin/activate"
exec env FLASK_APP="$DIR/app.py" flask run --port="$PORT"
