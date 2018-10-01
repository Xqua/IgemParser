import requests
import json
import re
from fuzzywuzzy import fuzz
import multiprocessing as mp
import pandas as pd

class Networks:
    def __init__(self, all_teams=None):
        if type(all_teams) == pd.core.frame.DataFrame:
            self.all_teams = all_teams
        else:
            all_teams = pd.read_csv('http://igem.org/Team_List.cgi?year=all&team_list_download=1')
            self.all_teams = all_teams.rename(columns={c: c.replace(' ', '') for c in all_teams.columns})

    def get_revision(self, year, pageid, rvstartid = None, counter = 0):
        try:
            if not rvstartid:
                url = "http://" + str(year) + ".igem.org/wiki/api.php?action=query&prop=revisions&pageids=" + str(pageid) + "&rvprop=size%7Ctimestamp%7Cuser%7Ccomment%7Cids%7Ccontent%7Csize&rvlimit=500&format=json&continue=||"
            else:
                url = "http://" + str(year) + ".igem.org/wiki/api.php?action=query&prop=revisions&pageids=" + str(pageid) + "&rvprop=size%7Ctimestamp%7Cuser%7Ccomment%7Cids%7Ccontent%7Csize&rvlimit=500&rvstartid=" + str(rvstartid) + "&format=json&continue=||"
            r = requests.get(url)
            j = json.loads(r.content)
            pages = j['query']['pages']
            revs = pages[list(pages.keys())[0]]['revisions']
            if "query-continue" in j.keys():
                rvstartid = j['query-continue']['revisions']['rvstartid']
            else:
                rvstartid = None
            return revs, rvstartid
        except:
            counter += 1
            if counter > 10:
                print("Error retrieving revisions for pageid: {} of year {}".format(pageid, year))
                return [], None
            else:
                self.get_revision(year, pageid, rvstartid = rvstartid, counter = counter)

    def get_revisions(self, year, pageid):
        revs, rvstartid = self.get_revision(year, pageid)
        while rvstartid:
            newrevs, rvstartid = self.get_revision(year, pageid, rvstartid=rvstartid)
            revs += newrevs
        return revs

    def clean_revisions(self, revisions):
        sections = []
        users = []
        timestamps = []
        sizes = []
        for rev in revisions:
            users.append(rev['user'])
            timestamps.append(rev['timestamp'])
            if 'size' in rev:
                sizes.append(rev['size'])
            else:
                sizes.append(0)
            sections.append(self.get_sections(rev))
        section_matching = self.define_unique_sections(sections)
        section_matching = self.match_sections_texts(sections, section_matching)
        cleaned = []
        for i in range(len(sections)):
            for j in range(len(sections[i])):
                sections[i][j]['id'] = section_matching[sections[i][j]['title']]
            cleaned.append({'user':users[i], 'ts':timestamps[i], 'size':sizes[i], 'sections':sections[i]})
        return cleaned

    def get_sections(self, rev):
        text = self.clean_html(rev['*'])
        lines = text.splitlines()
        title_search = re.compile('==.*==')
        sections = []
        element = {"title":"MainTextBody", "text":""}
        text = ""
        for i in range(len(lines)):
            matchs = title_search.findall(lines[i])
            if len(matchs) > 0:
                if ("===" in matchs[0]) or ("====" in matchs[0]) or ("=====" in matchs[0]):
                    pass
                else:
                    if element:
                        element['text'] = text
                        sections.append(element)
                    element = {'title':"", 'text':""}
                    text = ""
                    element['title'] = matchs[0].split('==')[1].strip()
            if element:
                text += lines[i]
        if element:
            element['text'] = text
            sections.append(element)
        return sections

    def define_unique_sections(self, all_sections):
        tmp = []
        for sections in all_sections:
            for section in sections:
                if section['title'] not in tmp:
                    tmp.append(section['title'])
        section_matching = {}
        index = 0
        for i in range(len(tmp)):
            for j in range(len(tmp)):
                if i >= j:
                    if fuzz.ratio(tmp[i], tmp[j]) > 90:
                        if tmp[i] in section_matching and not tmp[j] in section_matching:
                            section_matching[tmp[j]] = section_matching[tmp[i]]
                        if not tmp[i] in section_matching and tmp[j] in section_matching:
                            section_matching[tmp[i]] = section_matching[tmp[j]]
                        else:
                            section_matching[tmp[i]] = index
                            section_matching[tmp[j]] = index
                            index += 1
                    else:
                        if tmp[i] not in section_matching:
                            section_matching[tmp[i]] = index
                            index += 1
                        if tmp[j] not in section_matching:
                            section_matching[tmp[j]] = index
                            index += 1
        return section_matching

    def clean_html(self, html):
    	cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    	cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    	cleaned = re.sub(r"&nbsp;", " ", cleaned)
    	cleaned = re.sub(r"  ", " ", cleaned)
    	cleaned = re.sub(r"  ", " ", cleaned)
    	return cleaned.strip()

    def match_sections_texts(self, sections, section_matching, r_cutoff=80):
        for i in range(len(sections)-1):
            new_sections = [section_matching[section['title']] for section in sections[i]]
            for section_new in sections[i]:
                for section_old in sections[i+1]:
                    if section_matching[section_old['title']] not in new_sections:

                        r = fuzz.ratio(section_new['text'],section_old['text'])
                        if r > r_cutoff:
                            section_matching[section_old['title']] = section_matching[section_new['title']]
        return section_matching

    def multi_CPU_match_sections_texts(self, sections, section_matching, r_cutoff=80, CPU_nb=40):
        pool = mp.Pool(processes=CPU_nb)
        results = []
        for i in range(len(sections)-1):
            new_sections = [section_matching[section['title']] for section in sections[i]]
            for section_new in sections[i]:
                for section_old in sections[i+1]:
                    if section_matching[section_old['title']] not in new_sections:
                        results.append(pool.apply(self.text_fuzzy_match,
                                                        args=(section_new['text'],
                                                              section_old['text'],
                                                              r_cutoff,
                                                              section_old['title'],
                                                              section_new['title'])))
        for result in results:
            if result[0] == True:
                section_matching[result[1]] = section_matching[result[2]]
        pool.close()
        return section_matching

    def text_fuzzy_match(self, text1, text2, r_cutoff, title1, title2):
        r = fuzz.ratio(text1, text2)
        if r > r_cutoff:
            return (True, title1, title2)
        else:
            return (False, title1, title2)

    def check_diff(self, revisions):
        user_edits = []
        i = 0
        old_ids = []
        for i in range(len(revisions) - 1):
            user = revisions[i]['user']
            ts = revisions[i]['ts']
            size = revisions[i]['size']
            new_ids = []
            for section_new in revisions[i]['sections']:
                new_ids.append(section_new['id'])
                old_ids = []
                for section_old in revisions[i+1]['sections']:
                    old_ids.append(section_old['id'])
                    if section_old['id'] == section_new['id']:
                        if (section_old['text'] != section_new['text']) or (section_old['title'] != section_new['title']):
                            user_edits.append([user, i, section_new['id'], 'edit', ts, size])
            for old_id in old_ids:
                if old_id not in new_ids:
                    user_edits.append([user, i, old_id, 'delete', ts, size])
            for new_id in new_ids:
                if new_id not in old_ids:
                    user_edits.append([user, i, new_id, 'create', ts, size])
        for section in revisions[-1]['sections']:
            user = revisions[-1]['user']
            ts = revisions[-1]['ts']
            size = revisions[-1]['size']
            user_edits.append([user, i+1, section['id'], 'create', ts, size])
        return user_edits

    def get_edits(self, year, pageid, team):
        # print("Doing page {} of team {} / {}".format(pageid, team, year))
        revs = self.get_revisions(year, pageid)
        revisions = self.clean_revisions(revs)
        edits = self.check_diff(revisions)
        colabs = self.find_other_team(year, revs[0]['*'], team, pageid)
        return [edits, colabs]

    def get_pageslist(self, year, team, counter=0):
        url = "http://" + str(year) + ".igem.org/wiki/api.php?action=query&list=allpages&apprefix=Team:" + team + "&aplimit=max&format=json"
        try:
            r = requests.get(url)
            j = json.loads(r.content)
            pagestitles = []
            pagesids = []
            for page in j['query']['allpages']:
                pagestitles.append(page['title'])
                pagesids.append(page['pageid'])
            return {"pagesId":pagesids, "pagesTitle":pagestitles}
        except:
            counter += 1
            if counter > 10:
                print("Error on getting the pages of team: {}, year: {}".format(team, year))
                return {"pagesId":[], "pagesTitle":[]}
            else:
                self.get_pageslist(year, team, counter=counter)
        return {"pagesId":[], "pagesTitle":[]}

    def build_network_multithreads(self, year, team, CPU_nb=16):
        if year <= 2014 and year > 2010:
            if self.all_teams[(self.all_teams['Year'] == year) & (self.all_teams['Team'] == team)]['Section'].values[0] in ['High_school', 'IGEM']:
                year = str(year) + 'hs'
        pages = self.get_pageslist(year, team)
        if len(pages['pagesId']) == 0:
            if type(year) == str:
                year = int(year[:-2])
            pages = self.get_pageslist(year, team)
        IntraNetwork = []
        InterNetwork = []
        InterNetwork_refs = []
        self.collaborators = []
        self.ref_links = {}
        self.mentions={}
        pool = mp.Pool(processes=CPU_nb)
        results = []
        processes = []
        pagetitles = []
        for i in range(len(pages['pagesId'])):
            pageid = pages['pagesId'][i]
            if pageid:
                pagetitles.append(pages['pagesTitle'][i])
                processes.append(pool.apply_async(self.get_edits, args=(year, pageid, team)))
        for p in processes:
            try:
                results.append(p.get())
            except:
                pass
        # print("Parsed {} from team {}".format(len(results), team))
        # results = [p.get() for p in processes]
        # try:
        #     year = int(year)
        # except:
        #     year = int(year[:-2])
        if type(year) == str:
            year = int(year[:-2])
        collaborators = []
        ref_links = {}
        mentions={}
        i = 0
        for result in results:
            for edit in result[0]:
                IntraNetwork.append([year, team, pages['pagesId'][i], pages['pagesTitle'][i]] + edit)
            for collaborator in result[1][0]:
                if collaborator not in collaborators:
                    collaborators.append(collaborator)
                if collaborator not in mentions:
                    mentions[collaborator] = 0
                mentions[collaborator] += 1
            for collaborator in result[1][1]:
                if collaborator not in ref_links:
                    ref_links[collaborator] = []
                for el in result[1][1][collaborator]:
                    if el not in ref_links[collaborator]:
                        ref_links[collaborator].append([el, pages['pagesTitle'][i]])
            i += 1

        for team2 in collaborators:
            InterNetwork.append([year, team, team2, mentions[team2]])
            for link in ref_links[team2]:
                InterNetwork_refs.append([year, team, team2, link[0], link[1]])
        pool.close()
        return IntraNetwork, InterNetwork, InterNetwork_refs

    def build_network(self, year, team):
        pages = self.get_pageslist(year, team)
        IntraNetwork = []
        InterNetwork = []
        InterNetwork_refs = []
        collaborators = []
        ref_links = {}
        mentions={}
        results = []
        for i in range(len(pages['pagesId'])):
            pageid = pages['pagesId'][i]
            pagetitle = pages['pagesTitle'][i]
            # print("Doing: ", pageid)
            edits = self.get_edits(year, pageid, team)
            results.append(edits)

        collaborators = []
        ref_links = {}
        mentions={}
        i = 0
        for result in results:
            for edit in result[0]:
                IntraNetwork.append([year, team, pages['pagesId'][i], pages['pagesTitle'][i]] + edit)
            for collaborator in result[1][0]:
                if collaborator not in collaborators:
                    collaborators.append(collaborator)
                if collaborator not in mentions:
                    mentions[collaborator] = 0
                mentions[collaborator] += 1
            for collaborator in result[1][1]:
                if collaborator not in ref_links:
                    ref_links[collaborator] = []
                for el in result[1][1][collaborator]:
                    if el not in ref_links[collaborator]:
                        ref_links[collaborator].append([el, pages['pagesTitle'][i]])
            i += 1

        for team2 in collaborators:
            InterNetwork.append([year, team, team2, mentions[team2]])
            for link in ref_links[team2]:
                InterNetwork_refs.append([year, team, team2, link[0], link[1]])

        return IntraNetwork, InterNetwork, InterNetwork_refs

    def find_other_team(self, year, text, org_team, pageid):
        if type(year) == str:
            year = int(year[:-2])
        team_list = self.all_teams[(self.all_teams['Year'] == year) & (self.all_teams['Status'] == 'Accepted')]['Team'].tolist()
        team_list = [i for i in team_list if i != org_team]
        collaborators = []
        ref_links = {}
        for team in team_list:
            if self.advanced_search(team, text):
                collaborators.append(team)
                if team not in ref_links:
                    ref_links[team] = []
                ref_links[team].append(pageid)
        return collaborators, ref_links

    def advanced_search(self, team_name, wiki_text):
        names = [team_name]
        for char in ['_', '-']:
            names.append(team_name.replace(char, ' '))
        if team_name=='EPFL':
            names.append('EPF Lausanne')
        for name in names:
            if name in wiki_text:
                return True
        if self.fuzzy_search(team_name, wiki_text):
            return True
        return False

    def fuzzy_search(self, team_name, wiki_text, r_cutoff = 90):
        r = fuzz.partial_ratio(team_name, wiki_text)
        if r > r_cutoff:
            return True
        else:
            return False
