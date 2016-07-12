#!/bin/sh
# cd XXXX
if python wiki_crawler.py -v -y 2016 ; then
    echo "Command succeeded"
else
    echo "Command failed"
fi
timestamp=$(date +%s)
mv results/page_view_db.tsv results/page_view_db_$timestamp.tsv
