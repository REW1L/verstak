#!/bin/zsh

local docx=
if [ -n "$1" ]; then
    if [ "$1" = "-h" ]; then
        echo "usage: script.sh <path_to_file>"
        exit 0
    fi
    docx=$1
fi

if [ -n "${docx}" ]; then
    scp $1 truetnoth@95.217.164.47:~/verstak/docs/
fi

ssh -l truetnoth 95.217.164.47 "cd verstak && ./run.sh"
scp -r truetnoth@95.217.164.47:~/verstak/markdown .
scp -r truetnoth@95.217.164.47:~/verstak/html .

