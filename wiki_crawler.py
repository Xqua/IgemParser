#!/usr/bin/env python

import os
import pandas as pd
import wiki_parser as wp
import urllib
import urllib2
import sys
from boilerpipe.extract import Extractor
from optparse import OptionParser
from progressbar import Bar, ETA, Percentage, ProgressBar, Timer, Counter


parser = OptionParser()
parser.add_option("-p", "--pagelist", dest="PAGELIST", action="store_true",
                  help="Parse the team page list.")
parser.add_option("-r", "--results", dest="RESULTS", action="store_true",
                  help="Parse the team page list.")
parser.add_option("-i", "--infos", dest="INFOS", action="store_true",
                  help="Parse the team page list.")
parser.add_option("-c", "--contributions", dest="CONTRIBUTIONS", action="store_true",
                  help="Parse the team page list.")
parser.add_option("-v", "--pageview", dest="PAGEVIEW", action="store_true",
                  help="Parse the team page views.")
parser.add_option("-t", "--text", dest="TEXT", action="store_true",
                  help="Extract the team pages text.")
parser.add_option("-b", "--bioparts", dest="BIOPARTS", action="store_true",
                  help="Extract the team bioparts.")
parser.add_option("-d", "--redo", dest="REDO", action="store_true",
                  help="Relaunch parsing for team that had an error previously.")
parser.add_option("-y", "--years", dest="YEARS", default=None,
                  help="List of years to parse separated by a comma (ex: 2012,2016)")


# Parse options into variables
(options, args) = parser.parse_args()

PAGEVIEW = options.PAGEVIEW
RESULTS = options.RESULTS
BIOPARTS = options.BIOPARTS
INFOS = options.INFOS
CONTRIBUTIONS = options.CONTRIBUTIONS
PAGELIST = options.PAGELIST
TEXT = options.TEXT
REDO = options.REDO
YEARS = options.YEARS
if YEARS:
    YEARS = [i + '.csv' for i in YEARS.split(',')]

test = 0
for i in [PAGEVIEW, RESULTS, INFOS, CONTRIBUTIONS, PAGELIST, TEXT, BIOPARTS]:
    if i is True:
        test += 1
if test == 0:
    print "Please select at least one method, for help: ./wiki_crawler.py -h"
    sys.exit(1)

reload(sys)
sys.setdefaultencoding('utf8')

# naming conventions
# Team page
# http://igem.org/Team.cgi?team_id=1726
#
# Team Wikis
# http://[YEAR].igem.org/Team:[TEAM_NAME]
#
# User Contribs
# http://[YEAR].igem.org/wiki/index.php?title=Special:Contributions&limit=1000&target=[USERNAME]
#
# Team pages
# http://[YEAR].igem.org/wiki/index.php?title=Special%3APrefixIndex&prefix=Team%3A[TEAMNAME]&namespace=0
#
# Page Contrib
# http://[YEAR].igem.org/wiki/index.php?title=Team:[TEAMNAME]/[PAGENAME]&action=history
print """
---------------------------------------------------------
---------------------------------------------------------

"""


print """
 ___  ___________________   _____
|   |/  _____/\_   _____/  /     \.
|   /   \  ___ |    __)_  /  \ /  \.
|   \    \_\  \|        \/    Y    |
|___|\______  /_______  /\____|__  /
            \/        \/         \/
__________                   __               __
\______   \_______  ____    |__| ____   _____/  |_
 |     ___/\_  __ \/  _ \   |  |/ __ \_/ ___\   __|
 |    |     |  | \(  <_> )  |  \  ___/\  \___|  |
 |____|     |__|   \____/\__|  |\___  >\___  >__|
                        \______|    \/     \/

  _________ __                 __             .___
 /   _____//  |______ ________/  |_  ____   __| _/
 \_____  \|   __\__  \|_  __ \   __\/ __ \ / __ |
 /        \|  |  / __ \|  | \/|  | \  ___// /_/ |
/_______  /|__| (____  /__|   |__|  \___  >____ |
        \/           \/                 \/     \/  """

if not YEARS:
    years = os.listdir('Teams/good')
else:
    years = YEARS

# Storing which team have been done

log = file('log.log', 'w')
try:
    donelog = file('done.log', 'r')
    done = donelog.readlines()
    done = [int(i.strip()) for i in done]
    donelog.close()
except:
    done = []
print done
try:
    os.mkdir('results')
except:
    pass
# Opening the databases files
if PAGELIST:
    if REDO:
        teams_pages_db = file('results/team_pages_db.tsv', 'a')
    else:
        teams_pages_db = file('results/team_pages_db.tsv', 'w')
    teams_pages_db.write('TeamID\tWikiPages\n')

if BIOPARTS:
    bioparts_db = file('results/bioparts_db.tsv', 'w')
    bioparts_db.write('Year\tTeamID\tTeamName\tBioPart\tAuthor\n')

if RESULTS:
    if REDO:
        teams_results = file('results/team_results_db.tsv', 'a')
        teams_awards = file('results/team_awards_db.tsv', 'a')
    else:
        teams_results = file('results/team_results_db.tsv', 'w')
        teams_awards = file('results/team_awards_db.tsv', 'w')
    teams_results.write('Year\tTeamName\tMedal\tChampionship\tnb of awards\tFinalist\tWinner\n')
    teams_awards.write('Year\tTeamName\tAward\n')

if INFOS:
    if REDO:
        teams_info_db = file('results/teams_info_db.tsv', 'a')
    else:
        teams_info_db = file('results/teams_info_db.tsv', 'w')
    teams_info_db.write('TeamID\tTeamName\tTeamDesc\tTeamHSPrincipal\tTeamKind\tTeamDivision\tTeamRegion\tTeamCountry\tTeamSection\tTeamJambooree\tTeamTrack\tProjectTitle\tProjectAbstract\tPI_UID\tPI_Name\tSecondPI_UID\tSecondPI_Name\tInstructors_UID\tInstructors_Names\tStudentLeaders_UID\tStudentLeaders_Names\tStudentMembers_UID\tStudentMembers_Names\tAdvisors_UID\tAdvisors_Names\tPartNB_start\tPartNB_end\n')

# user_contributions_db = file('results/user_contributions_db.tsv', 'w')
# user_contributions_db.write('TeamID\tUserID\tPage\tDate\n')

if CONTRIBUTIONS:
    if REDO:
        page_contributions_db = file('results/page_contributions_db.tsv', 'a')
    else:
        page_contributions_db = file('results/page_contributions_db.tsv', 'w')
    page_contributions_db.write('TeamID\tPage\tDate\tUserID\tByteSize\n')

if PAGEVIEW:
    if REDO:
        page_view_db = file('results/page_view_db.tsv', 'a')
    else:
        page_view_db = file('results/page_view_db.tsv', 'w')
    page_view_db.write('Year\tPage\tPageView\n')

if TEXT:
    if REDO:
        teams_pages_text_db = file('results/team_pages_text_db.tsv', 'a')
    else:
        teams_pages_text_db = file('results/team_pages_text_db.tsv', 'w')
    teams_pages_text_db.write('Year\tTeamID\tPage\tPath\n')


def CleanHTML(html):
    """Clean HTML of potential tags that mess up with parsing."""
    html_escape_table = {
        "_-AND-_": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        ' ': '<BR>',
        ' ': '<br>',
    }
    for k in html_escape_table:
        html = html.replace(html_escape_table[k], k)
    return html


def PageView(y):
    """Parse the number of page view for a given year."""
    parser = wp.PageView()
    offset = 0
    while True:
        url = "http://%s.igem.org/wiki/index.php?title=Special:PopularPages&limit=5000&offset=%s" % (y, offset)
        handle = urllib2.urlopen(url)
        html = handle.read()
        if "There are no results for this report." in html.strip():
            break
        html = CleanHTML(html)
        parser.feed(html)
        pageviews = parser.res
        for i in pageviews:
            page_view_db.write(y + '\t' + '\t'.join(i) + '\n')
        f = open('results/%s/%s_PageView_%s.html' % (y, y, offset), 'w')
        f.write(html)
        f.close
        offset += 5000


def TeamPages(y, team, write=True):
    """Parse List of pages of a given team."""
    if int(y) >= 2015:
        parser = wp.TeamPagesList2015()
    else:
        parser = wp.TeamPagesList()
    url = "http://" + y + ".igem.org/wiki/index.php?title=Special%3APrefixIndex&prefix=Team%3A" + team + "&namespace=0"
    handle = urllib2.urlopen(url)
    html = handle.read()
    f = open('results/%s/%s/PageList.html' % (y, team), 'w')
    f.write(html)
    f.close()
    html = CleanHTML(html)
    parser.feed(html)
    pagelist = parser.res
    pagelist = [str(unicode(i).encode('utf8')) for i in pagelist]
    if write:
        for i in pagelist:
            teams_pages_db.write(str(teams_id[team_i]) + '\t' + i + '\n')
    return pagelist


def TeamInfo(y, team, team_i):
    """Parse Team Info CGI page."""
    parser = wp.TeamPage()
    url = "http://igem.org/Team.cgi?team_id=%s" % teams_id[team_i]
    os.remove('temp.html')
    os.system('wget %s -O temp.html -q' % url)
    f = open('temp.html')
    html = f.read()
    f.close()

    f = open('results/%s/%s/Team_Info.html' % (y, team), 'w')
    f.write(html)
    f.close()

    html = CleanHTML(html)
    parser.feed(html)
    team_info = parser.res
    if "Advisors" not in html.strip():
        team_info.insert(-2, 'None')
        team_info.insert(-2, 'None')
    if "Jamboree:" not in html.strip():
        print "no jamboree"
        team_info.insert(7, 'None')
    if "HS Principal:" not in html.strip():
        team_info.insert(2, 'None')
    # print len(team_info)
    user_list = []
    for k in [-4, -6, -8, -10, -12, -14]:
        if team_info[k] != 'None':
            user_list += team_info[k].split(';')
    # print "nb of users: ", len(user_list)
    teams_info_db.write(str(teams_id[team_i]) + '\t' + '\t'.join(team_info) + '\n')


def BiopartsTeamList(y, write=True):
    """Parse List of pages of a given team."""
    parser = wp.TeamListBioParts()
    url = "http://igem.org/Team_Parts?year=" + y
    handle = urllib2.urlopen(url)
    html = handle.read()
    # f = open('results/%s/BioParts_teamList.html' % (y), 'w')
    # f.write(html)
    # f.close()
    # html = CleanHTML(html)
    parser.feed(html)
    pagelist = parser.res
    res = []
    bar = ProgressBar(widgets=['Grabbing Biopart of year: %s ,,, Done:' % y, Counter(), '/', str(len(df)), Percentage(), Bar(), ETA(), '  ', Timer()])
    for i in bar(range(len(pagelist))):
        page = pagelist[i]
        team = page.split('=')[-1]
        res += Bioparts(page, y)
    if write:
        for i in res:
            i = [str(j) for j in i]
            bioparts_db.write(str(y) + '\t' + '\t'.join(i) + '\n')


def Bioparts(url, y):
    """Parse List of pages of a given team."""
    team = url.split('=')[-1]
    teamID = teamName2TeamID[team]
    parser = wp.TeamBioParts(team, teamID)
    handle = urllib2.urlopen(url)
    html = handle.read()
    # f = open('results/%s/%s/PageList.html' % (y, team), 'w')
    # f.write(html)
    # f.close()
    html = CleanHTML(html)
    parser.feed(html)
    biopartlist = parser.res
    return biopartlist


# def UserContrib(y, usr, team, team_i):
#     """Parse User Contribution page."""
#     if int(y) >= 2015:
#         parser = wp.UserContribution2015()
#     else:
#         parser = wp.UserContribution()
#     url = "http://" + y + ".igem.org/wiki/index.php?title=Special:Contributions&limit=1000&target=" + usr
#     # log.write(url)
#     handle = urllib2.urlopen(url)
#     html = handle.read()
#     if "No changes were found matching these criteria" not in html:
#         html = CleanHTML(html)
#         parser.feed(html)
#         contribs = parser.res
#         # log.write("Grabbed ! Result: %s" % contribs)
#         for X in contribs:
#             user_contributions_db.write(str(teams_id[team_i]) + '\t' + usr + '\t' + '\t'.join(X) + '\n')


def PageContrib(y, page, tp, team, team_i):
    """Parse contribnution of each pages, also called history of a page."""
    if int(y) >= 2015:
        parser = wp.PageContributions2015()
    else:
        parser = wp.PageContributions()
    upage = urllib.quote_plus(page)
    url = "http://" + y + ".igem.org/wiki/index.php?title=" + upage + "&action=history"
    # log.write(url)
    handle = urllib2.urlopen(url)
    html = handle.read()
    f = open('results/%s/%s/%s_-_-_History.html' % (y, team, page.replace('/', '#')), 'w')
    f.write(html)
    f.close()
    html = CleanHTML(html)
    parser.feed(html)
    contribs = parser.res
    tp += len(contribs)
    # log.write("Grabbed ! Result: %s" % contribs)
    for X in contribs:
        page_contributions_db.write(str(teams_id[team_i]) + '\t' + page + '\t' + '\t'.join(X) + '\n')
    return tp


def Results(y, division):
    """Parse the result page of IGEM."""
    if division not in ['high_school', 'igem', 'ent']:
        return False
    url = "http://igem.org/Results?year=" + y + "&name=Championship&division=" + division
    parser = wp.Results()
    handle = urllib2.urlopen(url)
    html = handle.read()
    f = open('results/%s/%s_Results_%s.html' % (y, y, division), 'w')
    f.write(html)
    f.close()
    html = CleanHTML(html)
    parser.feed(html)
    results = parser.res
    # print results
    for X in results:
        res = [y, X['teamName'], X['teamMedal'], X['teamChampionship'], len(X['teamAwards']), X['teamFinalist'], X['teamWinner']]
        res = [str(i) for i in res]
        teams_results.write('\t'.join(res) + '\n')
        for aw in X['teamAwards']:
            awa = [y, X['teamName'], aw]
            teams_awards.write('\t'.join(awa) + '\n')


def Text_extractor(y, page, team, team_i):
    """Extract the text of team pages using BoilerPipe."""
    upage = urllib.quote_plus(page)
    url = "http://" + y + ".igem.org/wiki/index.php?title=" + upage
    extractor = Extractor(extractor='ArticleExtractor', url=url)
    f = open('results/%s/%s/%s_-_-_CONTENT.html' % (y, team, page.replace('/', '#')), 'w')
    f.write(extractor.getHTML())
    f.close()
    f = open('results/%s/%s/%s_-_-_TEXT.html' % (y, team, page.replace('/', '#')), 'w')
    f.write(extractor.getText())
    f.close()
    path = 'results/%s/%s/%s_-_-_TEXT.html' % (y, team, page.replace('/', '#'))
    # text = text.replace('\\n', '\\\\n')
    output = '%s\t%s\t%s\t%s\n' % (y, str(teams_id[team_i]), page, path)
    teams_pages_text_db.write(output)


# iterate through all the years
for year in years:
    # We parse the data
    y = year.split('.')[0]
    print "Opening database for year: %s" % y
    df = pd.read_csv('Teams/good/%s' % year)
    teams = df[' Team  ']
    teams_id = df['Team ID ']
    teamName2TeamID = {}
    for i in range(len(teams_id)):
        teamName2TeamID[teams[i]] = teams_id[i]
    team_i = 0
    try:
        os.mkdir('results/%s' % y)
    except:
        pass
    if PAGEVIEW:
        PageView(y)

    if RESULTS:
        for div in ['high_school', 'igem', 'ent']:
            Results(y, div)

    if BIOPARTS:
        BiopartsTeamList(y)
    # we iterate throught all the teams
    if REDO:
        teams = [teams[i] for i in range(len(teams)) if teams_id[i] in done]
    for team in teams:
        try:
            os.mkdir('results/%s/%s' % (y, team))
        except:
            pass

        print "Doing team : %s of year %s" % (team, y)
        try:
            # we grab all the pages of the team
            if PAGELIST:
                pagelist = TeamPages(y, team)

            # Next we grab the user infos for this team
            if INFOS:
                user_list = TeamInfo(y, team, team_i)

            # # now we iterate through all users contributions (depreacated as contained in Page info)
            # for usr in user_list:
            #     UserContrib(y, usr, team, team_i)

            # Now we iterate throught all the pages
            tp = 0
            if CONTRIBUTIONS:
                if not PAGELIST:
                    pagelist = TeamPages(y, team, write=False)
                for page in pagelist:
                    tp = PageContrib(y, page, tp, team, team_i)
                # print "number of contribs: ", tp

            if TEXT:
                if not PAGELIST:
                    pagelist = TeamPages(y, team, write=False)
                for page in pagelist:
                    try:
                        Text_extractor(y, page, team, team_i)
                    except Exception as e:
                        print "Error accessing page: ", page
                        print e
        except Exception as e:
            print "ERROR !"
            print e
            print page
            donelog = file('done.log', 'a')
            donelog.write(str(teams_id[team_i]) + '\n')
            donelog.close()
        team_i += 1

# teams_pages_db.close()

# teams_info_db.close()

# user_contributions_db.close()

# page_contributions_db.close()

print """
---------------------------------------------------------
---------------------------------------------------------
.___  ___________________   _____
|   |/  _____/\_   _____/  /     \.
|   /   \  ___ |    __)_  /  \ /  \.
|   \    \_\  \|        \/    Y    |
|___|\______  /_______  /\____|__  /
            \/        \/         \/
__________                   __               __
\______   \_______  ____    |__| ____   _____/  |_
 |     ___/\_  __ \/  _ \   |  |/ __ \_/ ___\   __|
 |    |     |  | \(  <_> )  |  \  ___/\  \___|  |
 |____|     |__|   \____/\__|  |\___  >\___  >__|
                        \______|    \/     \/      """

print '============================================================'
print '============================================================'
print '============================================================'
print '====VICTORY==VICTORY==VICTORY==VICTORY==VICTORY==VICTORY===='
print '============================================================'
print '==================IGEM  HAS  BEEN  CRAWLED=================='
print '==================IGEM  HAS  BEEN  PARSED==================='
print '============================================================'
print '=== \o/ \o/ \o/ \o/ \o/ \o/      \o/ \o/ \o/ \o/ \o/ \o/ ==='
print '============================================================'
print '============================================================'
