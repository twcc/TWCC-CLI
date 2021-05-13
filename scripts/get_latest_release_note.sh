#!/bin/bash

CMD=`grep -hnr "### v" README.md | sed 's/:### v/ /' | awk '/ /{print $1}' | head -n 2 |paste -sd " " -  | awk '/ /{print "cat README.md | head -n " $2-1  " | tail  -" $2-$1}'`
eval $CMD
