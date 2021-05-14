#!/bin/bash

CMD=`grep -hnr "### v" README.md | sed 's/:### v/ /' | awk '/ /{print $1}' | head -n 2 |paste -sd " " -  | awk '/ /{print $1-1 " " $2}'`
python -c "import sys; begin=int(sys.argv[1]); end=int(sys.argv[2]); stm=open('README.md', 'r').readlines(); print('\\n'.join([ x.strip() for x in stm[begin:end]]))" $CMD
