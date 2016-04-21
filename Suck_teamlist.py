#!/usr/bin/env python

import os

for i in range(2008, 2016 + 1):
    os.system("wget 'http://igem.org/Team_List.cgi?year=%s&division=igem&team_list_download=1' -O %s.csv" % (i, i))
