#!/usr/bin/env python

import os
import pandas as pd
import wiki_parser as wp
import urllib
import urllib2
import sys

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

print """.___  ___________________   _____
|   |/  _____/\_   _____/  /     \
|   /   \  ___ |    __)_  /  \ /  \
|   \    \_\  \|        \/    Y    |
|___|\______  /_______  /\____|__  /
            \/        \/         \/ """
print """__________                   __               __
\______   \_______  ____    |__| ____   _____/  |_
 |     ___/\_  __ \/  _ \   |  |/ __ \_/ ___\   __|
 |    |     |  | \(  <_> )  |  \  ___/\  \___|  |
 |____|     |__|   \____/\__|  |\___  >\___  >__|
                        \______|    \/     \/      """

print """  _________ __                 __             .___
 /   _____//  |______ ________/  |_  ____   __| _/
 \_____  \|   __\__  \|_  __ \   __\/ __ \ / __ |
 /        \|  |  / __ \|  | \/|  | \  ___// /_/ |
/_______  /|__| (____  /__|   |__|  \___  >____ |
        \/           \/                 \/     \/  """


years = os.listdir('Teams/good')

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
teams_pages_db = file('results/team_pages_db.tsv', 'w')
teams_pages_db.write('TeamID\tWikiPages\n')

teams_info_db = file('results/teams_info_db.tsv', 'w')
teams_info_db.write('TeamID\tTeamName\tTeamDesc\tTeamHSPrincipal\tTeamKind\tTeamDivision\tTeamRegion\tTeamCountry\tTeamSection\tTeamJambooree\tTeamTrack\tProjectTitle\tProjectAbstract\tPI_UID\tPI_Name\tSecondPI_UID\tSecondPI_Name\tInstructors_UID\tInstructors_Names\tStudentLeaders_UID\tStudentLeaders_Names\tStudentMembers_UID\tStudentMembers_Names\tAdvisors_UID\tAdvisors_Names\tPartNB_start\tPartNB_end\n')

# user_contributions_db = file('results/user_contributions_db.tsv', 'w')
# user_contributions_db.write('TeamID\tUserID\tPage\tDate\n')

page_contributions_db = file('results/page_contributions_db.tsv', 'w')
page_contributions_db.write('TeamID\tPage\tDate\tUserID\tByteSize\n')

page_view_db = file('results/page_view_db.tsv', 'w')
page_view_db.write('Year\tPage\tPageView\n')


def CleanHTML(html):
    html_escape_table = {
        "_-AND-_": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
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


def TeamPages(y, team):
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


def UserContrib(y, usr, team, team_i):
    """Parse User Contribution page."""
    if int(y) >= 2015:
        parser = wp.UserContribution2015()
    else:
        parser = wp.UserContribution()
    url = "http://" + y + ".igem.org/wiki/index.php?title=Special:Contributions&limit=1000&target=" + usr
    # log.write(url)
    handle = urllib2.urlopen(url)
    html = handle.read()
    if "No changes were found matching these criteria" not in html:
        html = CleanHTML(html)
        parser.feed(html)
        contribs = parser.res
        # log.write("Grabbed ! Result: %s" % contribs)
        for X in contribs:
            user_contributions_db.write(str(teams_id[team_i]) + '\t' + usr + '\t' + '\t'.join(X) + '\n')


def PageContrib(y, page, tp, team, team_i):
    """Parce contribnution of each pages, also called history of a page."""
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


# iterate through all the years
for year in years:
    # We parse the data
    y = year.split('.')[0]
    print "Opening database for year: %s" % y
    df = pd.read_csv('Teams/good/%s' % year)
    teams = df[' Team  ']
    teams_id = df['Team ID ']
    team_i = 0
    try:
        os.mkdir('results/%s' % y)
    except:
        pass
    PageView(y)

    # we iterate throught all the teams
    for team in teams:
        try:
            os.mkdir('results/%s/%s' % (y, team))
        except:
            pass

        print "Doing team : %s of year %s" % (team, y)
        try:
            # we grab all the pages of the team
            pagelist = TeamPages(y, team)

            # Next we grab the user infos for this team
            user_list = TeamInfo(y, team, team_i)

            # # now we iterate through all users contributions (depreacated as contained in Page info)
            # for usr in user_list:
            #     UserContrib(y, usr, team, team_i)

            # Now we iterate throught all the pages
            tp = 0
            for page in pagelist:
                tp = PageContrib(y, page, tp, team, team_i)
                # print "number of contribs: ", tp
        except Exception as e:
            print "ERROR !"
            print e
            donelog = file('done.log', 'a')
            donelog.write(str(teams_id[team_i]) + '\n')
            donelog.close()

        team_i += 1

teams_pages_db.close()

teams_info_db.close()

# user_contributions_db.close()

page_contributions_db.close()


print """.___  ___________________   _____
|   |/  _____/\_   _____/  /     \
|   /   \  ___ |    __)_  /  \ /  \
|   \    \_\  \|        \/    Y    |
|___|\______  /_______  /\____|__  /
            \/        \/         \/ """
print """__________                   __               __
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
