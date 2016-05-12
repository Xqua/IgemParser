#!/usr/bin/env python

import pandas as pd
from sqlalchemy import create_engine  # database connection

page_contrib = pd.read_cvs('results/page_contributions_db.tsv', sep='\t')
page_view = pd.read_cvs('results/page_view_db.tsv', sep='\t')
team_pages = pd.read_cvs('results/team_pages_db.tsv', sep='\t')
teams_info = pd.read_cvs('results/teams_info_db.tsv', sep='\t')

disk_engine = create_engine('sqlite:///IGEM.db')

chunksize = 20000

page_contrib.to_sql('page_contributions', disk_engine, chunksize=chunksize)
page_view.to_sql('page_view', disk_engine, chunksize=chunksize)
team_pages.to_sql('teams_pages', disk_engine, chunksize=chunksize)
teams_info.to_sql('teams_metadata', disk_engine, chunksize=chunksize)
