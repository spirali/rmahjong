#!/bin/sh
cd `dirname $0`
exec python3 server.py $1
