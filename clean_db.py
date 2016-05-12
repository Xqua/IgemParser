#!/usr/bin/evn python

import os
import pandas as pd

years = os.listdir('Teams/good')


page_view = pd.read_csv('results/page_view_db.tsv', sep='\t')
page_contrib = pd.read_csv('results/page_contributions_db.tsv', sep='\t')
team_pages = pd.read_csv('results/team_pages_db.tsv', sep='\t')
teams_info = pd.read_csv('results/teams_info_db.tsv', sep='\t')

team_names = {}
for year in years:
    df = pd.read_csv('Teams/good/' + year)
    df = df.rename(columns={c: c.replace(' ', '') for c in df.columns})
    for i in range(len(df)):
        tID = df['TeamID'][i]
        t = df['Team'][i]
        team_names[t] = tID

res = []
for i in range(len(page_view)):
    p = page_view['Page'][i]
    # print p
    if p[0] == '/':
        p = p[1:]
        page_view['Page'][i] = p
    if '.igem.org' in p:
        # print "replace"
        p = p.replace('2008.igem.org/wiki/index.php?', '')
        p = p.replace('2009.igem.org/wiki/index.php?', '')
        p = p.replace('2010.igem.org/wiki/index.php?', '')
        p = p.replace('2011.igem.org/wiki/index.php?', '')
        p = p.replace('2012.igem.org/wiki/index.php?', '')
        p = p.replace('2013.igem.org/wiki/index.php?', '')
        p = p.replace('2014.igem.org/wiki/index.php?', '')
        p = p.replace('2015.igem.org/wiki/index.php?', '')
        p = p.replace('2016.igem.org/wiki/index.php?', '')

        p = p.replace('2008.igem.org/', '')
        p = p.replace('2009.igem.org/', '')
        p = p.replace('2010.igem.org/', '')
        p = p.replace('2011.igem.org/', '')
        p = p.replace('2012.igem.org/', '')
        p = p.replace('2013.igem.org/', '')
        p = p.replace('2014.igem.org/', '')
        p = p.replace('2015.igem.org/', '')
        p = p.replace('2016.igem.org/', '')
        page_view['Page'][i] = p
    if 'Wiki' in p.split('/')[0]:
        if len(p.split('/')) > 1:
            if 'Team:' in p.split('/')[1]:
                p = p.replace('Wiki/', '')
                page_view['Page'][i] = p
    if 'Team:' in p:
        n = p.split('/')[0].split(':')[1]
        try:
            tID = team_names[n]
        except:
            try:
                tID.replace(' ', '_')
                tID = team_names[n]
            except:
                "bad luck"
        res.append(tID)
    else:
        res.append(0)

page_view['TeamID'] = pd.Series(res, index=page_view.index)

page_view.to_csv('results/page_view_db_cleaned.tsv', sep='\t', index=False)
