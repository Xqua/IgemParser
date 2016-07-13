#!/bin/sh
# cd XXXX
if python wiki_crawler.py -v -y 2016 ; then
    echo "Command succeeded"
else
    curl -X POST --data-urlencode 'payload={"text":"IGEM pageView parsing encountered an error !"}' https://commonground.xqua.org/hooks/SHxgYKqkQ6AkeTiMQ/YfjgCsRNrcFGrsMZFD3htn2YPSByukj5JPQb8FoPNgpDXPgp
fi
day_ts = `cat old_ts`  
timestamp=$(date +%s)
xdelta delta page_view_db_$day_ts.tsv page_view_db.tsv page_view_db_$timestamp.patch
tar -uf results/page_view_db_$timestamp.tar page_view_db_$timestamp.patch
rm page_view_db_$timestamp.patch

