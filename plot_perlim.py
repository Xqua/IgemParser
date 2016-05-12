#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import datetime
from scipy import stats

df = pd.read_csv('page_contributions_db.tsv', sep='\t')
contribs = df['TeamID'].tolist()
contribs = np.array(contribs)
unique, counts = np.unique(contribs, return_counts=True)

sns.set(style="whitegrid", palette="pastel", color_codes=True)
plt.figure()
plt.title('distribution of number of contributions per teams')
sns.violinplot(y=counts, cut=0)

maxe = {}
for i in range(len(df)):
    team = df['TeamID'][i]
    try:
        date = datetime.datetime.strptime(df['Date'][i], "%Y-%m-%dT%H:%M:%S")
        if team not in maxe:
            maxe[team] = date
        else:
            if maxe[team] < date:
                maxe[team] = date
    except:
        pass

date_distrib = {}

for i in range(len(df)):
    team = df['TeamID'][i]
    try:
        date = datetime.datetime.strptime(df['Date'][i], "%Y-%m-%dT%H:%M:%S")
        if team not in date_distrib:
            date_distrib[team] = []
        date_distrib[team].append((maxe[team] - date).total_seconds())
    except:
        pass

x = date_distrib.keys()
y = np.array([date_distrib[i] for i in x])
y2 = [np.std(i) / np.mean(i) for i in y]
y3 = [stats.entropy(i) for i in y]

plt.figure()
plt.title('distribution std over mean nb of contrib per team')
sns.violinplot(data=y2, cut=0)
plt.figure()
plt.title('distribution shanon entropy of contrib per team')
sns.violinplot(data=y3, cut=0)

for b in range(3):
    for i in range(3):
        np.random.shuffle(y)
        plt.figure()
        sns.violinplot(data=y[: 30], cut=0)


plt.show()

# for k in date_distrib:
#     sns.violinplot(y=date_distrib[team], cut=0)
#     plt.show()
