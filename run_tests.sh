#!/bin/bash

# Colors (the ones we use)
CGRN="\033[32m"
CRED="\033[31m"
CEND="\033[0m"
FBOLD="\033[1m"

if [[ $* == *--help* ]] || [ "$1" == "-h" ]; then
    echo "Usage: $0 [--help, --cov, --edited]]"
    echo "--help will print this message"
    echo "--cov with print a coverage report"
    echo "--edited will limmit test to the files changed but not yet commited"
    exit 0
fi


# Initial message
message(){
    echo ""
    echo -e "${CRED}Above is a list of errors detected in your code. ${FBOLD}Please fix them before committing!${CEND}"
    echo -e "You can bypass this check (and incur Ace's wrath) with \'git commit --no-verify\'"
}

trap message 0

# Find working directory + add it to $PYTHONPATH
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )" # Resolve $SOURCE until its no longer a symlink
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # If $SOURCE is relative, resolve it relative to the symlink
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
echo $DIR
export PYTHONPATH=$DIR

# Show errors in bash
set -e

# Run pep8 (Python linter) + unit tests
if hash pep8 2>/dev/null; then
    if [[ $* == *--edited* ]]; then
        cd $DIR
        for i in $( git diff --name-only HEAD ); do
            extension="${i##*.}"
            if [ "$extension" == "py" ]; then
                pep8 $i --ignore=E122,E241,W293,W291,W391,E501,E126
            fi
        done
    else
        pep8 $DIR/src --ignore=E122,E241,W293,W291,W391,E501,E126
        pep8 $DIR/src_test --ignore=E122,E241,W293,W291,W391,E501,E126
    fi
else
    echo -e "${CRED}${FBOLD}Error: pep8 not found.${CEND}"
    exit 1
fi
if hash py.test 2>/dev/null; then
        py.test $DIR/src $DIR/src_test
    else
        echo -e "${CGRN}${FBOLD}Error: pytest not found.${CEND}"
        exit 1
fi
trap - 0
echo -e "${CGRN}All tests ran!${CEND}"

# Run code coverage analysis
if [[ $* == *--cov* ]] ; then
    if $(command py.test --cov src/server src_test >/dev/null 2>&1); then
        py.test --cov $DIR/src/server $DIR/src_test/server
        py.test --cov $DIR/src/vis $DIR/src_test/vis
        py.test --cov $DIR/src/mapgen $DIR/src_test/mapgen
        py.test --cov $DIR/src/objects $DIR/src_test/objects
    else
        echo "Cant find pytest-cov plugin"
        exit 1
    fi
fi

# Install pre-commit hook
FILE="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
HOOKPATH=$DIR/".git/hooks/pre-commit"
if [ ! -L $HOOKPATH ]; then
    echo "Installing pre-commit hook..."
    # Remove old hook file
    if  [ -f $HOOKPATH ]; then
        rm $HOOKPATH
    fi
    # Symlink to new hook file
    ln -s $DIR/$FILE $HOOKPATH
    echo "Pre-commit hoook installed!"
fi

# Done!
echo -e "${CGRN}${FBOLD}Done!${CEND}"
