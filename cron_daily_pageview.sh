#!/bin/sh

cd XXX

day_ts = `cat old_ts`  
gzip results/page_view_db_$day_ts.tar
rm page_view_db_$day_ts.tsv

if python wiki_crawler.py -v -y 2016 ; then
    echo "Command succeeded"
else
    curl -X POST --data-urlencode 'payload={"text":"IGEM pageView parsing encountered an error !"}' https://commonground.xqua.org/hooks/SHxgYKqkQ6AkeTiMQ/YfjgCsRNrcFGrsMZFD3htn2YPSByukj5JPQb8FoPNgpDXPgp
fi
timestamp=$(date +%s)
mv results/page_view_db.tsv results/page_view_db_$timestamp.tsv


tar -cvf results/page_view_db_$timestamp.tar results/page_view_db_$timestamp.tsv

echo $timestamp > old_ts

