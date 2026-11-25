#!/bin/bash
# porównanie błędów ESLint (bez numerów linii) między dwiema wersjami: wypisuje tylko nowe
cd /tmp/lint
for f in "$1" "$2"; do python3 extract.py "$f" /tmp/lint/$(basename $f).js; done
a=/tmp/lint/$(basename $1).js; b=/tmp/lint/$(basename $2).js
npx eslint --no-eslintrc -c .eslintrc.json -f unix "$a" 2>/dev/null | sed -E 's/^[^:]+:[0-9]+:[0-9]+: //' | sort > /tmp/lint/A.txt
npx eslint --no-eslintrc -c .eslintrc.json -f unix "$b" 2>/dev/null | sed -E 's/^[^:]+:[0-9]+:[0-9]+: //' | sort > /tmp/lint/B.txt
echo "błędów: stara $(wc -l < A.txt), nowa $(wc -l < B.txt)"
comm -13 A.txt B.txt | head -30
[ -z "$(comm -13 A.txt B.txt)" ] && echo "(brak różnic)"
