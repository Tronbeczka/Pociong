#!/bin/bash
# pełna regresja: ./runall.sh plik.html wynik.txt
cd /tmp/pwt; APP=$1; OUT=$2; : > $OUT
for t in t_core t_lanes t_junc t_hold t_gest; do
  s=$(date +%s); r=$(APP=$APP timeout 700 python3 $t.py 2>&1); e=$(( $(date +%s)-s ))
  echo "$r" > out/$t.log
  echo "$t ${e}s :: $(echo "$r" | grep WYNIK) :: FAILS=$(echo "$r" | grep -c '^FAIL') TB=$(echo "$r" | grep -c Traceback)" >> $OUT
  echo "$r" | grep '^FAIL' | cut -c1-250 >> $OUT
done
echo ALLDONE >> $OUT
