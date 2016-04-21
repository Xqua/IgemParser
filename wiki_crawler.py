#!/usr/bin/env python

import os
import pandas as pd
import wiki_parser as wp
import urllib2

years = os.listdir('Teams')

#Opening the databases files
teams_pages_db = file('team_pages_db.tsv')
teams_pages_db.write('TeamID\tWikiPages\n')

teams_info_db = file('teams_info_db.tsv')
teams_info_db.write('TeamID\tTeamName\tTeamDesc\tTeamKind\tTeamDivision\tTeamRegion\tTeamCountry\tTeamSection\tProjectTitle\tProjectAbstract\tPI_UID\tPI_Name\tSecondPI_UID\tSecondPI_Name\tInstructors_UID\tInstructors_Names\tStudentLeaders_UID\tStudentLeaders_Names\tStudentMembers_UID\tStudentMembers_Names\tAdvisors_UID\tAdvisors_Names\n')
user_contributions_db = file('user_contributions_db.tsv')
user_contributions_db.write('TeamID\tUserID\tPage\tDate\n')
page_contributions_db = file('page_contributions_db.tsv')
page_contributions_db.write('TeamID\tUserID\tPage\tDate\tByteSize\n')


# iterate through all the years
for year in years:
    # We parse the data
    y = year.split('.')[0]
    df = pd.read_csv('Teams/%s' % year)
    teams = df[' Team  ']
    teams_id = df['Team ID ']
    team_i = 0
    # we iterate throught all the teams
    for team in teams:
        # we grab all the pages of the team
        parser = wp.TeamPagesList()
        url = "http://"+y+".igem.org/wiki/index.php?title=Special%3APrefixIndex&prefix=Team%3A"+team+"&namespace=0"
        handle = urllib2.urlopen(url)
        html = handle.read()
        parser.feed(html)
        pagelist = parser.res
        teams_pages_db.write(teams_id[team_i] + '\t' + ';'.join(pagelist) + '\n')

        # Next we grab the user infos for this team
        parser = wp.TeamPage()
        url = "http://igem.org/Team.cgi?team_id=%s"%teams_id[team_i]
        handle = urllib2.urlopen(url)
        html = handle.read()
        parser.feed(html)
        team_info = parser.res
        user_list = team_info[-4].split(';')
        teams_info_db.write(teams_id[team_i] + '\t' + '\t'.join(team_info) + '\n')

        # now we iterate through all users contributions
        for usr in user_list:
            parser = wp.UserContribution()
            url = "http://"+ y +".igem.org/wiki/index.php?title=Special:Contributions&limit=1000&target=" + usr
            handle = urllib2.urlopen(url)
            html = handle.read()
            parser.feed(html)
            contribs = parser.res
            for X in contribs:
                user_contributions_db.write(teams_id[team_i] + '\t' + usr + '\t' + '\t'.join(X) + '\n')

        # Now we iterate throught all the pages
        for page in pagelist:
            parser = wp.PageContributions()
            url = "http://"+ y +".igem.org/wiki/index.php?title=Team:PennState/Project&action=history"

