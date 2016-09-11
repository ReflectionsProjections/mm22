#!/bin/bash

# View Turn script from mm20; should work for mm21 with a few minor changes
# It assumes that:
# 1) one line = one turn
# 2) the first turn contains the connection info
# If you ask for a turn beyond the last one, it will display end of game info

if [ "$1" == "-h" ]; then
  echo "Usage: $0 turn_number (If zero, displays connection info.)"
  exit 0
fi
let turn=$1+1
head -n $turn gamerunner/log.json | tail -n 1 | python -m json.tool | less
