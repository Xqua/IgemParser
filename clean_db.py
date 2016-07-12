#!/usr/bin/evn python

import os
import pandas as pd

years = os.listdir('Teams/good')


page_view = pd.read_csv('results/page_view_db.tsv', sep='\t')
page_contrib = pd.read_csv('results/page_contributions_db.tsv', sep='\t')
team_pages = pd.read_csv('results/team_pages_db.tsv', sep='\t')
teams_info = pd.read_csv('results/teams_info_db.tsv', sep='\t')
team_result = pd.read_csv('results/team_results_db.tsv', sep='\t')
team_awards = pd.read_csv('results/team_awards_db.tsv', sep='\t')
teams_meta = pd.DataFrame()


team_names = {}
for year in years:
    y = year.split('.')[0]
    if y not in team_names:
        team_names[y] = {}
    df = pd.read_csv('Teams/good/' + year)
    df = df.rename(columns={c: c.replace(' ', '') for c in df.columns})
    teams_meta = pd.concat([teams_meta, df])
    for i in range(len(df)):
        tID = df['TeamID'][i]
        t = df['Team'][i].replace(' ', '_')
        team_names[y][t] = tID

res = []
for i in range(len(team_result)):
    y = str(team_result['Year'][i])
    t = team_result['TeamName'][i]
    print y, t
    tID = team_names[y][t]
    res.append(tID)

team_result['TeamID'] = pd.Series(res, index=team_result.index)

res = []
for i in range(len(team_awards)):
    y = str(team_awards['Year'][i])
    t = team_awards['TeamName'][i]
    print y, t
    tID = team_names[y][t]
    res.append(tID)

team_awards['TeamID'] = pd.Series(res, index=team_awards.index)

tID2Y = {}
for y in team_names.keys():
    for t in team_names[y].keys():
        tID2Y[team_names[y][t]] = y

res = []
for i in range(len(page_contrib)):
    tID = page_contrib['TeamID'][i]
    res.append(tID2Y[tID])

page_contrib['Year'] = pd.Series(res, index=page_contrib.index)

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

page_view = page_view.drop_duplicates()
page_contrib = page_contrib.drop_duplicates()
team_pages = team_pages.drop_duplicates()
teams_info = teams_info.drop_duplicates()

page_view.to_csv('results/page_view_db_cleaned.tsv', sep='\t', index=False)
page_contrib.to_csv('results/page_contributions_db.tsv', sep='\t', index=False)
team_pages.to_csv('results/team_pages_db.tsv', sep='\t', index=False)
teams_info.to_csv('results/teams_info_db.tsv', sep='\t', index=False)
team_result.to_csv('results/team_results_db.tsv', sep='\t', index=False)
team_awards.to_csv('results/team_awards_db.tsv', sep='\t', index=False)
teams_meta.to_csv('results/team_meta_db.tsv', sep='\t', index=False)
