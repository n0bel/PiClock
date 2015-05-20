#!/bin/sh
# taken from input_map.sh from lircd distribution
# http://www.lirc.org/

TYPES="KEY BTN"
file=${1:-/usr/include/linux/input.h}

# Use gnu-sed on Macosx
if test "`uname`" = 'Darwin'; then
  SED=gsed
else
  SED=sed
fi

for type in $TYPES; do
        grep "^#define ${type}_" < $file|sort|$SED -n --expression="s/^#define \([^ \t]*\)[ \t][ \t]*\([0-9][0-9a-fA-FxX]*\).*/{\"\1\", \2},/p"
done
