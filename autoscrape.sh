#! /usr/bin/env bash

DATE=$(date -I)
DATETIME=$(date +%Y-%m-%d_%H-%M)
OUTFILE="$(realpath $1)/$DATETIME.json"
OUTLINK="$(realpath $1)/$DATE.json"

cd $(dirname $(realpath $0))
make scrape OUTFILE=$OUTFILE
if [[ -s $OUTFILE ]]
then
    ln -f "$OUTFILE" "$OUTLINK"
else
    rm $OUTFILE
fi
