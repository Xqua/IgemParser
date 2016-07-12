#!/usr/bin/env python

import pandas as pd
from sqlalchemy import create_engine  # database connection

page_contrib = pd.read_csv('results/page_contributions_db.tsv', sep='\t')
page_view = pd.read_csv('results/page_view_db.tsv', sep='\t')
team_pages = pd.read_csv('results/team_pages_db.tsv', sep='\t')
teams_info = pd.read_csv('results/teams_info_db.tsv', sep='\t')

page_contrib.to_csv('results/page_contributions_db.tsv', sep='\t', index=False)
page_view.to_csv('results/page_view_db.tsv', sep='\t', index=False)
team_pages.to_csv('results/team_pages_db.tsv', sep='\t', index=False)
teams_info.to_csv('results/teams_info_db.tsv', sep='\t', index=False)


disk_engine = create_engine('sqlite:///IGEM.db')

chunksize = 20000

page_contrib.to_sql('page_contributions', disk_engine, chunksize=chunksize)
page_view.to_sql('page_view', disk_engine, chunksize=chunksize)
team_pages.to_sql('teams_pages', disk_engine, chunksize=chunksize)
teams_info.to_sql('teams_metadata', disk_engine, chunksize=chunksize)
