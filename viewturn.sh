#!/bin/bash

# Recreation of Sam Laane's script for mm20 turn-viewing
# @author ace-n

# Get log.json location
logPath=$(find . -name log.json)

# Get nth line of file
line=$(sed -n $1p < $logPath)

# Prettify it
echo $line | python -m json.tool
