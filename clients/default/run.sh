#!/bin/bash
if hash python2 2>/dev/null; then
        python2 client.py $1 $2
    else
        python client.py $1 $2
    fi
