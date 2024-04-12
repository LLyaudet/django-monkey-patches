#!/bin/bash
sed -Ez 's/(\[[a-zA-Z0-9:-]*\]: [^\n\\]*)\\\n/\1/Mg'\
  README_printable.md > README_temp.md
sed -Ez 's/(\[[a-zA-Z0-9:-]*\]: [^\n\\]*)\\\n/\1/Mg'\
  README_temp.md > README.md
rm -f README_temp.md

