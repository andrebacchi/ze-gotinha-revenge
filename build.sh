#!/bin/sh
# Gera index.html e sw.js (ou dist/artifact.html com "sh build.sh artifact").
cd "$(dirname "$0")" && python3 build.py "$@"
