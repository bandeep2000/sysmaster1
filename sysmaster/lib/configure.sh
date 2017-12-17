#!/bin/bash
echo "adding python lib path to bashrc"
path=`pwd`
file="$HOME/.bashrc"
echo " "  >>$file
echo "PYTHONPATH=\$HOME/lib/python:$path" >>$file
echo "export PYTHONPATH" >>$file
#source $file

echo "please run \"source $file\""

