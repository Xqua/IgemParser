#!/usr/bin/env python

import os
import sys

if not os.path.isdir('pageViews2016'):
    os.mkdir('pageViews2016')

arch_path = sys.argv[1]
name = arch_path.split('.')[0]

if not os.path.isdir(name):
    os.mkdir(name)
os.system('tar zxvf %s -C ./%s' % (arch_path, name))

lfiles = os.listdir('./' + name)

main = [i for i in lfiles if 'tsv' in i][0]
patches = [i for i in lfiles if 'patch' in i]

for patch in patches:
    ts = patch.split('.')[0].split('_')[-1]
    n = 'page_view_db_%s.tsv' % ts
    cmd = 'xdelta patch %s %s %s' % (os.path.join(name, patch), os.path.join(name, main), os.path.join(name, n))
    os.system(cmd)
