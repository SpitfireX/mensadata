#! /usr/bin/env bash

DATE=$(date -I)
DATETIME=$(date +%Y-%m-%d_%H-%M)
OUTFILE="$(realpath $1)/$DATETIME.json"
OUTLINK="$(realpath $1)/$DATE.json"

make scrape OUTFILE=$OUTFILE
ln -f "$OUTFILE" "$OUTLINK"
