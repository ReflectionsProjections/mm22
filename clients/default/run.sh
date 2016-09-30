#!/bin/bash
if hash python2 2>/dev/null; then
        python2 test_client.py $1 $2
    else
        python test_client.py $1 $2
    fi
