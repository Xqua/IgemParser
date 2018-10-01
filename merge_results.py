#!/usr/bin/env python3

import pandas as pd
from optparse import OptionParser
import sys, os


parser = OptionParser()
parser.add_option("-r", "--result-folders", action="append", dest="folders", default=[],
                  help="result folder to merge. -r folder1 -r folder2 etc")
parser.add_option("-o", "--out-path", action="store", dest="out", default="merged_results",
                  help="out folder path to store merged_results into.")
parser.add_option("-c", "--check", dest="check", action="store_true",
                  help="Compare number of team to registered number of teams per year.")


# Parse options into variables
(options, args) = parser.parse_args()

if len(options.folders) < 2:
    print("Need at least two folder to merge.")
    sys.exit(1)

if options.check:
    all_teams = pd.read_csv('http://igem.org/Team_List.cgi?year=all&team_list_download=1')
    all_teams = all_teams.rename(columns={c: c.replace(' ', '') for c in all_teams.columns})

folders = options.folders
# Define all the files:
db_files = [
    "bioparts_db.tsv",
    "internetwork_db.tsv",
    "internetwork_refs_db.tsv",
    "intranetwork_db.tsv",
    "team_awards_db.tsv",
    # "team_pages_db.tsv",
    "team_results_db.tsv",
    "teams_info_members_db.tsv",
    "teams_info_meta_db.tsv"
    ]

if not os.path.isdir(options.out):
    os.mkdir(options.out)

databases = {}

for folder in folders:
    for db in db_files:
        print("Opening: {}/{}".format(folder, db))
        if db not in databases:
            databases[db] = pd.read_table(os.path.join(folder, db))
        else:
            tmp = pd.read_table(os.path.join(folder, db))
            print("years in db:", tmp['Year'].unique())
            databases[db] = databases[db].append(tmp)

for db in db_files:
    databases[db] = databases[db].drop_duplicates()
    databases[db].to_csv(os.path.join(options.out, db), sep='\t', index=False)
    if options.check:
        print("Checking file:", db)
        for y in all_teams['Year'].unique():
            if y not in databases[db]['Year'].unique():
                print("Missing year: ", y)
        for y in databases[db]['Year'].unique():
            print("year: {}, teams in db/igem:{}/{}".format(y,
                                              len(databases[db][databases[db]['Year'] == y]['Team'].unique()),
                                              len(all_teams[(all_teams['Year'] == y) & (all_teams['Status'] == 'Accepted')]['Team'].unique())) )
