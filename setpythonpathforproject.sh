#!/bin/bash

#sets the project base and runs a command

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo ""
    echo "Usage: $0 [--help] command"
    echo "--help will print this message"
    echo "runs the command with the python path set to make imports easy"
    echo "example usage $0 python"
    echo "If you get an import error with python trying running your command with this"
    echo "*** for debugging only ***"
    echo "Ultimately The main game runner should be made to set things up correctly without this."
    echo ""

    exit 0
fi

# Find working directory + add it to $PYTHONPATH
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )" # Resolve $SOURCE until its no longer a symlink
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # If $SOURCE is relative, resolve it relative to the symlink
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
echo "with with base at $DIR"
export PYTHONPATH=$DIR

# run the command
$*
