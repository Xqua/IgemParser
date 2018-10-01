#!/usr/bin/env python

import os
import pandas as pd
import wiki_parser as wp
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import sys
from boilerpipe.extract import Extractor
from optparse import OptionParser
from progressbar import Bar, ETA, Percentage, ProgressBar, Timer, Counter, FormatCustomText
from networks import Networks

parser = OptionParser()
parser.add_option("-p", "--pagelist", dest="PAGELIST", action="store_true",
                  help="Parse the team page list.")
parser.add_option("-r", "--results", dest="RESULTS", action="store_true",
                  help="Parse the team page list.")
parser.add_option("-i", "--infos", dest="INFOS", action="store_true",
                  help="Parse the team page list.")
# parser.add_option("-c", "--contributions", dest="CONTRIBUTIONS", action="store_true",
#                   help="Parse the team page list.")
parser.add_option("-v", "--pageview", dest="PAGEVIEW", action="store_true",
                  help="Parse the team page views.")
parser.add_option("-t", "--text", dest="TEXT", action="store_true",
                  help="Extract the team pages text.")
parser.add_option("-b", "--bioparts", dest="BIOPARTS", action="store_true",
                  help="Extract the team bioparts.")
parser.add_option("-n", "--networks", dest="NETWORKS", action="store_true",
                  help="Extract the intra and inter team network data.")
parser.add_option("-a", "--append", dest="REDO", action="store_true",
                  help="Append to already existing database files.")
parser.add_option("-y", "--years", dest="YEARS", default="",
                  help="List of years to parse separated by a comma (ex: 2012,2016)")


# Parse options into variables
(options, args) = parser.parse_args()

PAGEVIEW = options.PAGEVIEW
RESULTS = options.RESULTS
BIOPARTS = options.BIOPARTS
INFOS = options.INFOS
# CONTRIBUTIONS = options.CONTRIBUTIONS
PAGELIST = options.PAGELIST
TEXT = options.TEXT
REDO = options.REDO
YEARS = options.YEARS
NETWORKS = options.NETWORKS


test = 0
for i in [PAGEVIEW, RESULTS, INFOS, PAGELIST, TEXT, BIOPARTS, NETWORKS]:
    if i is True:
        test += 1
if test == 0:
    print("Please select at least one method, for help: ./wiki_crawler.py -h")
    sys.exit(1)

#reload(sys)
#sys.setdefaultencoding('utf8')

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
print("""
---------------------------------------------------------
---------------------------------------------------------

""")


print("""
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
        \/           \/                 \/     \/  """)

# Storing which team have been done

log = open('log.log', 'w')
try:
    donelog = open('done.log', 'r')
    done = donelog.readlines()
    done = [int(i.strip()) for i in done]
    donelog.close()
except:
    done = []

print(done)

if not os.path.isdir('./results'):
    os.mkdir('results')

# Opening the databases opens
if PAGELIST:
    if REDO:
        teams_pages_db = open('results/team_pages_db.tsv', 'a')
    else:
        teams_pages_db = open('results/team_pages_db.tsv', 'w')
    teams_pages_db.write('TeamID\tWikiPages\n')

if BIOPARTS:
    if REDO:
        bioparts_db = open('results/bioparts_db.tsv', 'a')
    else:
        bioparts_db = open('results/bioparts_db.tsv', 'w')
        bioparts_db.write('Year\tTeamID\tTeam\tBioPart\tAuthor\n')

if NETWORKS:
    if REDO:
        intranetwork_db = open('results/intranetwork_db.tsv', 'a')
        internetwork_db = open('results/internetwork_db.tsv', 'a')
        internetwork_refs_db = open('results/internetwork_refs_db.tsv', 'a')
    else:
        intranetwork_db = open('results/intranetwork_db.tsv', 'w')
        internetwork_db = open('results/internetwork_db.tsv', 'w')
        internetwork_refs_db = open('results/internetwork_refs_db.tsv', 'w')
        intranetwork_db.write('Year\tTeam\tPageId\tPageTitle\tUserID\tEditId\tSectionId\tActionType\tTimeStamp\tByteSize\n')
        internetwork_db.write('Year\tTeam\tTarget\tNbOfMention\n')
        internetwork_refs_db.write('Year\tTeam\tTarget\tPageId\tPageTitle\n')

if RESULTS:
    if REDO:
        teams_results = open('results/team_results_db.tsv', 'a')
        teams_awards = open('results/team_awards_db.tsv', 'a')
    else:
        teams_results = open('results/team_results_db.tsv', 'w')
        teams_awards = open('results/team_awards_db.tsv', 'w')
    teams_results.write('Year\tTeam\tTeamID\tMedal\tChampionship\tnb of awards\tFinalist\tWinner\n')
    teams_awards.write('Year\tTeam\tTeamID\tAward\n')

if INFOS:
    if REDO:
        teams_info_members_db = open('results/teams_info_members_db.tsv', 'a')
        teams_info_meta_db = open('results/teams_info_meta_db.tsv', 'a')
    else:
        teams_info_members_db = open('results/teams_info_members_db.tsv', 'w')
        teams_info_meta_db = open('results/teams_info_meta_db.tsv', 'w')
    teams_info_members_db.write('Year\tTeamID\tTeam\tMemberType\tUserID\tUserName\n')
    teams_info_meta_db.write('Year\tTeamID\tTeam\tMetaType\tMetaData\n')
    # teams_info_db.write('TeamID\tTeamName\tTeamDesc\tTeamHSPrincipal\tTeamKind\tTeamDivision\tTeamRegion\tTeamCountry\tTeamSection\tTeamJambooree\tTeamTrack\tProjectTitle\tProjectAbstract\tPI_UID\tPI_Name\tSecondPI_UID\tSecondPI_Name\tInstructors_UID\tInstructors_Names\tStudentLeaders_UID\tStudentLeaders_Names\tStudentMembers_UID\tStudentMembers_Names\tAdvisors_UID\tAdvisors_Names\tPartNB_start\tPartNB_end\n')

# user_contributions_db = open('results/user_contributions_db.tsv', 'w')
# user_contributions_db.write('TeamID\tUserID\tPage\tDate\n')
#
# if CONTRIBUTIONS:
#     if REDO:
#         page_contributions_db = open('results/page_contributions_db.tsv', 'a')
#     else:
#         page_contributions_db = open('results/page_contributions_db.tsv', 'w')
#     page_contributions_db.write('TeamID\tPage\tDate\tUserID\tByteSize\n')

if PAGEVIEW:
    if REDO:
        page_view_db = open('results/page_view_db.tsv', 'a')
    else:
        page_view_db = open('results/page_view_db.tsv', 'w')
    page_view_db.write('Year\tPage\tPageView\n')

if TEXT:
    if REDO:
        teams_pages_text_db = open('results/team_pages_text_db.tsv', 'a')
    else:
        teams_pages_text_db = open('results/team_pages_text_db.tsv', 'w')
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
    if type(html) == bytes:
        html = html.decode('utf8', 'ignore')
    for k in html_escape_table:
        html = html.replace(html_escape_table[k], k)
    return bytes(html.encode('utf8'))


def PageView(y):
    """Parse the number of page view for a given year."""
    parser = wp.PageView()
    offset = 0
    while True:
        url = "http://%s.igem.org/wiki/index.php?title=Special:PopularPages&limit=5000&offset=%s" % (y, offset)
        handle = urllib.request.urlopen(url)
        html = handle.read()
        if b"There are no results for this report." in html.strip():
            break
        html = CleanHTML(html)
        parser.feed(html.decode('utf8', 'ignore'))
        pageviews = parser.res
        for i in pageviews:
            page_view_db.write(y + '\t' + '\t'.join(i) + '\n')
        f = open('results/%s/%s_PageView_%s.html' % (y, y, offset), 'w')
        f.write(html.decode('utf8', 'ignore'))
        f.close
        offset += 5000


def TeamPages(y, team, write=True, counter = 0):
    """Parse List of pages of a given team."""
    # print("Parsing team page list ...")
    try:
        if int(y) >= 2015:
            parser = wp.TeamPagesList2015()
        else:
            parser = wp.TeamPagesList()
        url = "http://" + y + ".igem.org/wiki/index.php?title=Special%3APrefixIndex&prefix=Team%3A" + team + "&namespace=0"
        handle = urllib.request.urlopen(url)
        html = handle.read()
        f = open('results/%s/%s/PageList.html' % (y, team), 'w')
        f.write(html.decode('utf8','ignore'))
        f.close()
        html = CleanHTML(html)
        parser.feed(html.decode('utf8', 'ignore'))
        pagelist = parser.res
        if write:
            for i in pagelist:
                teams_pages_db.write(str(teams_id[team_i]) + '\t' + i + '\n')
        return pagelist
        # pagelist = [i.encode('utf8') for i in pagelist]
    except:
        counter += 1
        if counter > 10:
            print("Failed to read the page for team {}".format(team))
            return []
        TeamPages(y, team, write=True, counter = counter)


def TeamInfo(y, team, team_i):
    """Parse Team Info CGI page."""
    parser = wp.TeamInfo(y, team, teams_id[team_i])

    results = parser.parse_team(teams_id[team_i])
    members = parser.make_member_table(results)
    meta = parser.make_team_table(results)

    for el in members:
        teams_info_members_db.write('\t'.join([str(i) for i in el]) + '\n')
    for el in meta:
        teams_info_meta_db.write('\t'.join([str(i) for i in el]) + '\n')

    # teams_info_db.write(str(teams_id[team_i]) + '\t' + '\t'.join(team_info) + '\n')

    # parser = wp.TeamPage()
    # url = "http://igem.org/Team.cgi?team_id=%s" % teams_id[team_i]
    # if os.path.isfile('temp.html'):
    #     os.remove('temp.html')
    # os.system('wget %s -O temp.html -q' % url)
    # f = open('temp.html', 'rb')
    # html = f.read()
    # html = html.decode('utf8', 'ignore')
    # f.close()
    # if os.path.isfile('temp.html'):
    #     os.remove('temp.html')
    # f = open('results/%s/%s/Team_Info.html' % (y, team), 'w')
    # f.write(html)
    # f.close()
    #
    # html = CleanHTML(html)
    # parser.feed(html.decode('utf8', 'ignore'))
    # team_info = parser.res
    # if b"Advisors" not in html.strip():
    #     team_info.insert(-2, 'None')
    #     team_info.insert(-2, 'None')
    # if b"Jamboree:" not in html.strip():
    #     # print("no jamboree")
    #     team_info.insert(7, 'None')
    # if b"HS Principal:" not in html.strip():
    #     team_info.insert(2, 'None')
    # # print len(team_info)
    # user_list = []
    # for k in [-4, -6, -8, -10, -12, -14]:
    #     if team_info[k] != 'None':
    #         user_list += team_info[k].split(';')
    # # print "nb of users: ", len(user_list)
    # teams_info_db.write(str(teams_id[team_i]) + '\t' + '\t'.join(team_info) + '\n')


def BiopartsTeamList(y, write=True, counter = 0):
    """Parse List of pages of a given team."""
    try:
        parser = wp.TeamListBioParts()
        url = "http://igem.org/Team_Parts?year=" + y
        handle = urllib.request.urlopen(url)
        html = handle.read()
    except:
        counter += 1
        if counter > 10:
            print("Failed to read bioparts for year {}".format(y))
            return None
        BiopartsTeamList(y, write=True, counter = counter)
    # f = open('results/%s/BioParts_teamList.html' % (y), 'w')
    # f.write(html)
    # f.close()
    # html = CleanHTML(html)
    parser.feed(html.decode('utf8', 'ignore'))
    pagelist = parser.res
    res = []
    bar = ProgressBar(widgets=['Grabbing Biopart of year: %s ,,, Done:' % y, Counter(), '/', str(len(pagelist)), Percentage(), Bar(), ETA(), '  ', Timer()], redirect_stdout=True)
    for i in bar(list(range(len(pagelist)))):
        page = pagelist[i]
        team = page.split('=')[-1]
        if team != 'Example':
            ret = Bioparts(page, y)
            if ret:
                res += ret
    if write:
        for i in res:
            i = [str(j).replace('\t', ' ').strip() for j in i]
            bioparts_db.write(str(y) + '\t' + '\t'.join(i) + '\n')


def Bioparts(url, y, counter = 0):
    """Parse List of pages of a given team."""
    team = url.split('=')[-1]
    teamID = teamName2TeamID[team]
    parser = wp.TeamBioParts(team, teamID)
    try:
        handle = urllib.request.urlopen(url)
        html = handle.read()
        html = CleanHTML(html)
        parser.feed(html.decode('utf8', 'ignore'))
        biopartlist = parser.res
        return biopartlist
    except:
        if counter > 10:
            print("Error for url: ", url)
            return None
        else:
            counter += 1
            Bioparts(url, y, counter)



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

#
# def PageContrib(y, page, tp, team, team_i, counter=0):
#     """Parse contribnution of each pages, also called history of a page."""
#     if int(y) >= 2015:
#         parser = wp.PageContributions2015()
#     else:
#         parser = wp.PageContributions()
#     upage = urllib.parse.quote_plus(page)
#     url = "http://" + y + ".igem.org/wiki/index.php?title=" + upage + "&action=history"
#     # print(url)
#     # log.write(url)
#     try:
#         handle = urllib.request.urlopen(url)
#         html = handle.read()
#         f = open('results/%s/%s/%s_-_-_History.html' % (y, team, page.replace('/', '#')), 'w')
#         f.write(html.decode('utf8','ignore'))
#         f.close()
#         html = CleanHTML(html)
#         # print(html)
#         parser.feed(html.decode('utf8', 'ignore'))
#         contribs = parser.res
#         # print(contribs)
#         tp += len(contribs)
#         # log.write("Grabbed ! Result: %s" % contribs)
#         for X in contribs:
#             page_contributions_db.write(str(teams_id[team_i]) + '\t' + page + '\t' + '\t'.join(X) + '\n')
#         return tp
#     except:
#         counter += 1
#         PageContrib(y, page, tp, team, team_i, counter=counter)
#         if counter > 10:
#             print("Error in parsing ")
#             return tp


def Results(y, division, counter = 0):
    """Parse the result page of IGEM."""
    if division not in ['high_school', 'igem', 'ent']:
        return False
    try:
        url = "http://igem.org/Results?year=" + y + "&name=Championship&division=" + division
        parser = wp.Results()
        handle = urllib.request.urlopen(url)
        html = handle.read()
    except:
        counter += 1
        if counter > 10:
            print("Error getting the result page for division {}".format(division))
            return None
        Results(y, division, counter = counter)
    f = open('results/%s/%s_Results_%s.html' % (y, y, division), 'w')
    f.write(html.decode('utf8', 'ignore'))
    f.close()
    html = CleanHTML(html)
    parser.feed(html.decode('utf8', 'ignore'))
    results = parser.res
    # print results
    for X in results:
        try:
            res = [y, X['teamName'], teamName2TeamID[X['teamName']], X['teamMedal'], X['teamChampionship'], len(X['teamAwards']), X['teamFinalist'], X['teamWinner']]
            res = [str(i) for i in res]
            teams_results.write('\t'.join(res) + '\n')
            for aw in X['teamAwards']:
                # print "good", teamName2TeamID[X['teamName']]
                awa = [y, X['teamName'], str(teamName2TeamID[X['teamName']]),  aw]
                teams_awards.write('\t'.join(awa) + '\n')
        except:
            print(("Error for:", X['teamName']))

def Text_extractor(y, page, team, team_i, counter=0):
    """Extract the text of team pages using BoilerPipe."""
    try:
        upage = urllib.parse.quote_plus(page)
        url = "http://" + y + ".igem.org/wiki/index.php?title=" + upage
        extractor = Extractor(extractor='ArticleExtractor', url=url)
    except:
        counter += 1
        if counter > 10:
            print("Failed to get the text for page {}".format(page))
            return None
        Text_extractor(y, page, team, team_i, counter=counter)
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
print("Loading team databases ...")
all_teams = pd.read_csv('http://igem.org/Team_List.cgi?year=all&team_list_download=1')
all_teams = all_teams.rename(columns={c: c.replace(' ', '') for c in all_teams.columns})

if YEARS:
    years = [int(i) for i in YEARS.split(',')]
else:
    years = all_teams['Year'].unique()

if NETWORKS:
    Networks = Networks(all_teams)
# print(YEARS)
# print(years)

for y in years:
    if y not in all_teams['Year'].unique():
        continue
    if y < 2008:
        continue
    # We parse the data
    # y = year.split('.')[0]
    print(("Grabbing team list for year: %s" % y))
    # df = pd.read_csv('Teams/%s' % year)
    df = all_teams[(all_teams['Year'] == y) & (all_teams['Status'] == 'Accepted')]
    teams = df['Team'].values
    teams_id = df['TeamID'].values
    teamName2TeamID = {}
    for i in range(len(teams_id)):
        teamName2TeamID[teams[i]] = teams_id[i]
    team_i = 0
    try:
        os.mkdir('results/%s' % y)
    except:
        pass

    y = str(y)

    if PAGEVIEW:
        PageView(y)

    if RESULTS:
        print("Parsing Results page ...")
        if int(y) < 2014:
            for div in ['high_school', 'igem', 'ent']:
                Results(y, div)
        elif int(y) == 2014:
            for div in ['high_school', 'igem']:
                Results(y, div)
        else:
            Results(y, 'igem')
    if BIOPARTS:
        BiopartsTeamList(y)
    # we iterate throught all the teams
    # if REDO:
    #     teams = [teams[i] for i in range(len(teams)) if teams_id[i] in done]

    team_tasks = FormatCustomText(
        'Team: %(team)s, Task: %(task)s | ',
        dict(
            team="none",
            task="none",
        ),
    )

    bar = ProgressBar(widgets=['Parsing year %s. ' % y,
                               team_tasks,
                               Counter(), '/', str(len(teams)),
                               Percentage(),
                               Bar(),
                               ETA(),
                               '  ',
                               Timer()
                               ], max_value=len(teams), redirect_stdout=True)
    for team in teams:
        pagelist = None
        team_tasks.update_mapping(team=team)
        bar.update(team_i)
        try:
            os.mkdir('results/%s/%s' % (y, team))
        except:
            pass

        # print(("Doing team : %s of year %s" % (team, y)))
#        try:
            # we grab all the pages of the team
        if PAGELIST:
            team_tasks.update_mapping(task="Parsing page list")
            bar.update(team_i)
            pagelist = TeamPages(y, team)

        # Next we grab the user infos for this team
        if INFOS:
            team_tasks.update_mapping(task="Users infos")
            bar.update(team_i)
            user_list = TeamInfo(y, team, team_i)

        # # now we iterate through all users contributions (depreacated as contained in Page info)
        # for usr in user_list:
        #     UserContrib(y, usr, team, team_i)

        # Now we iterate throught all the pages
        tp = 0
        # if CONTRIBUTIONS:
        #     if not PAGELIST or not pagelist:
        #         team_tasks.update_mapping(task="Parsing page list")
        #         bar.update(team_i)
        #         pagelist = TeamPages(y, team, write=False)
        #     team_tasks.update_mapping(task="Users contributions")
        #     bar.update(team_i)
        #     for page in pagelist:
        #         # page = page[2:-1]
        #         tp = PageContrib(y, page, tp, team, team_i)
        #     # print "number of contribs: ", tp

        if NETWORKS:
            team_tasks.update_mapping(task="Parsing networks")
            bar.update(team_i)
            IntraNet, InterNet, InterNetRefs = Networks.build_network_multithreads(int(y), team)
            for el in IntraNet:
                intranetwork_db.write("\t".join([str(el_i) for el_i in el]) + '\n')
            for el in InterNet:
                internetwork_db.write("\t".join([str(el_i) for el_i in el]) + '\n')
            for el in InterNetRefs:
                internetwork_refs_db.write("\t".join([str(el_i) for el_i in el]) + '\n')

        if TEXT:
            if not PAGELIST or not pagelist:
                team_tasks.update_mapping(task="Parsing page list")
                bar.update(team_i)
                pagelist = TeamPages(y, team, write=False)
            team_tasks.update_mapping(task="Wiki pages texts")
            bar.update(team_i)
            for page in pagelist:
                if type(page) == bytes:
                    page = page.decode(encoding='UTF-8')
                # page = page.decode('utf8')
                try:
                    Text_extractor(y, page, team, team_i)
                except Exception as e:
                    print(("Error accessing page: ", page))
                    print(e)
#        except Exception as e:
#            print("ERROR !")
#            print(e)
#            #print(page)
#            donelog = open('done.log', 'a')
#            donelog.write(str(teams_id[team_i]) + '\n')
#            donelog.close()
        team_i += 1


# Opening the databases opens
if PAGELIST:
    teams_pages_db.close()

if BIOPARTS:
        bioparts_db.close()

if NETWORKS:
        intranetwork_db.close()
        internetwork_db.close()
        internetwork_refs_db.close()

if RESULTS:
    teams_results.close()
    teams_awards.close()

if INFOS:
    teams_info_members_db.close()
    teams_info_meta_db.close()

if PAGEVIEW:
    page_view_db.close()

if TEXT:
    teams_pages_text_db.close()

# if TEXT:
#     os.system("python n-gram_extract.py")
print("Cleaning the databases ... please wait !")

def Clean_pageviews(p):
    if p[0] == '/':
        p = p[1:]
    if '.igem.org' in p:
        for y in years:
            p = p.replace('{}.igem.org/wiki/index.php?' % y, '')
            p = p.replace('{}.igem.org/' % y, '')
    if 'Wiki' in p.split('/')[0]:
        if len(p.split('/')) > 1:
            if 'Team:' in p.split('/')[1]:
                p = p.replace('Wiki/', '')
    return p

# def CleanByteSize(b):
#     t = 0
#     try:
#         t = b.replace('(','').replace(')','').replace('bytes','').replace('byte','').replace(',','')
#         t = int(t)
#     except:
#         if b == 'empty':
#             t = 0
#         else:
#             print(t)
#             print(b)
#     return t

if os.path.isfile('results/page_view_db.tsv'):
    page_view = pd.read_csv('results/page_view_db.tsv', sep='\t')
# if os.path.isfile('results/page_contributions_db.tsv'):
#     page_contrib = pd.read_csv('results/page_contributions_db.tsv', sep='\t')
if os.path.isfile('results/team_pages_db.tsv'):
    team_pages = pd.read_csv('results/team_pages_db.tsv', sep='\t')
if os.path.isfile('results/teams_info_db.tsv'):
    teams_info = pd.read_csv('results/teams_info_db.tsv', sep='\t')
if os.path.isfile('results/team_results_db.tsv'):
    team_result = pd.read_csv('results/team_results_db.tsv', sep='\t')
if os.path.isfile('results/team_awards_db.tsv'):
    team_awards = pd.read_csv('results/team_awards_db.tsv', sep='\t')
if os.path.isfile('results/intranetwork_db.tsv'):
    intranetwork = pd.read_csv('results/intranetwork_db.tsv', sep='\t')
teams_meta = all_teams

teams = all_teams['Team']
teamIDs = all_teams['TeamID'].values
years = all_teams['Year'].values
team_names = {}
for i in range(len(teams)):
    if years[i] not in team_names:
        team_names[years[i]] = {}
    team_names[years[i]][teams[i]] = teamIDs[i]

tID2Y = {}
for y in list(team_names.keys()):
    for t in list(team_names[y].keys()):
        tID2Y[team_names[y][t]] = y

if os.path.isfile('results/team_results_db.tsv'):
    team_result['TeamID'] = team_result.apply(lambda x: team_names[x['Year']][x['TeamName']] , axis=1)
    team_result.to_csv('results/team_results_db.tsv', sep='\t', index=False)
if os.path.isfile('results/team_awards_db.tsv'):
    team_awards['TeamID'] = team_awards.apply(lambda x: team_names[x['Year']][x['TeamName']] , axis=1)
    team_awards.to_csv('results/team_awards_db.tsv', sep='\t', index=False)
# if os.path.isfile('results/page_contributions_db.tsv'):
#     page_contrib['Year'] = page_contrib.apply(lambda x: tID2Y[x['TeamID']] , axis=1)
#     page_contrib['ByteSize'] = page_contrib['ByteSize'].apply(CleanByteSize)
#     page_contrib = page_contrib.drop_duplicates()
#     page_contrib.to_csv('results/page_contributions_db.tsv', sep='\t', index=False)
if os.path.isfile('results/page_view_db.tsv'):
    page_view['TeamID'] = page_view['Page'].apply(Clean_pageviews)
    page_view = page_view.drop_duplicates()
    page_view.to_csv('results/page_view_db_cleaned.tsv', sep='\t', index=False)
if os.path.isfile('results/team_pages_db.tsv'):
    team_pages = team_pages.drop_duplicates()
    team_pages.to_csv('results/team_pages_db.tsv', sep='\t', index=False)
if os.path.isfile('results/teams_info_db.tsv'):
    teams_info = teams_info.drop_duplicates()
    teams_info.to_csv('results/teams_info_db.tsv', sep='\t', index=False)
if os.path.isfile('results/intranetwork_db.tsv'):
    intranetwork = intranetwork.drop_duplicates()
    intranetwork.to_csv('results/intranetwork_db.tsv', sep='\t', index=False)

teams_meta.to_csv('results/team_meta_db.tsv', sep='\t', index=False)


# os.system("python clean_db.py")
# teams_pages_db.close()

# teams_info_db.close()

# user_contributions_db.close()

# page_contributions_db.close()

print("""
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
                        \______|    \/     \/      """)

print( '============================================================')
print( '============================================================')
print( '============================================================')
print( '====VICTORY==VICTORY==VICTORY==VICTORY==VICTORY==VICTORY====')
print( '============================================================')
print( '==================IGEM  HAS  BEEN  CRAWLED==================')
print( '==================IGEM  HAS  BEEN  PARSED===================')
print( '============================================================')
print( '=== \o/ \o/ \o/ \o/ \o/ \o/      \o/ \o/ \o/ \o/ \o/ \o/ ===')
print( '============================================================')
print( '============================================================')
