from HTMLParser import HTMLParser
from datetime import datetime

# create a subclass and override the handler methods


class TeamPagesList(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
        self.date = False
        self.id = 0
        self.tmp = []
        self.res = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # if self.start:
        # print "Encountered a start tag:", tag
        # print attrs
        if tag == 'table':
            if 'id' in attrs:
                if attrs['id'] == "mw-prefixindex-list-table":
                    self.start = True
                    # print "START"

        if tag == 'a' and self.start:
            self.res.append(attrs['title'].replace('_-AND-_', '&'))
            # print 'tmp', self.res

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        if tag == 'table' and self.start:
            self.start = False

    # def handle_data(self, data):
        # print "Encountered some data  :", data


class TeamPagesList2015(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
        self.date = False
        self.id = 0
        self.tmp = []
        self.res = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # if self.start:
        # print "Encountered a start tag:", tag
        # print attrs
        if tag == 'table':
            if 'class' in attrs:
                if attrs['class'] == "mw-prefixindex-list-table":
                    self.start = True
                    # print "START"

        if tag == 'a' and self.start:
            self.res.append(attrs['title'].replace('_-AND-_', '&'))
            # print 'tmp', self.res

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        if tag == 'table' and self.start:
            self.start = False


class TeamPage(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
        self.start2 = False
        self.start_end = False
        self.start_pi = False
        self.start_2pi = False
        self.start_inst = False
        self.start_leader = False
        self.start_advisor = False
        self.start_parts = False
        self.record = False
        self.record_pre = False
        self.id = 0
        self.tmp = []
        self.tmp2 = []
        self.res = []
        self.i = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # if self.start:
        # print "Encountered a start tag:", tag
        # print attrs

        if tag == 'table':
            if 'id' in attrs:
                if attrs['id'] == "table_info":
                    self.start = True
                    # print "START"
        if tag == 'table':
            if 'id' in attrs:
                if attrs['id'] == "table_abstract":
                    self.start2 = True
                    # print "START2"

        if tag == 'tr' and self.start:
            self.record = True

        if tag == 'pre' and self.start:
            self.record_pre = True

        if tag == 'td' and self.start2:
            self.record = True

        if tag == 'a' and self.start_pi:
            # print "start pi Rec true"
            self.record = True

        if tag == 'a' and self.start_inst:
            # print "start inst Rec true"
            self.record = True

        if tag == 'a' and self.start_leader:
            self.record = True
            self.tmp = []
            self.tmp2 = []
            self.i = 0

        if self.start_pi and self.record and tag == 'tr':
            # print "Stop PI"
            self.start_pi = False
            self.record = False
        if self.start_2pi and self.record and tag == 'tr':
            # print "Stop PI2"
            self.start_2pi = False
            self.record = False

        if tag == 'tr' and self.start_2pi:
            # print "start pi 2 Rec true"
            self.record = True
            self.tmp = []
            self.tmp2 = []
            self.i = 0

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        if tag == 'table' and self.start:
            self.start = False
        if tag == 'table' and self.start2:
            self.start2 = False
            # self.res.append(self.tmp)
            # print 'res', self.res

        if self.start_end and tag == "table":
            self.start_end = False
            self.record = False
            self.res.append(";".join(self.tmp))
            self.res.append(";".join(self.tmp2))
        if self.start_advisor and tag == "table":
            self.start_advisor = False
            self.res.append(";".join(self.tmp))
            self.res.append(";".join(self.tmp2))

    def handle_data(self, data):
        # print "Encountered some data  :", data
        data = data.replace('\n', ' ')
        data = data.replace('\r', ' ')
        data = data.replace('\t', ' ')
        data = data.replace('_-AND-_', '&')
        # print "record", self.record
        if self.start and self.record_pre:
            self.res.append(data.strip())
            self.record_pre = False
            self.record = False
        if self.start and self.record:
            if ':' not in data:
                self.res.append(data.strip())
                self.record = False
        if "Assigned Track" in data:
            self.res.append(data.strip().split(':')[1])
        if " has not been assigned to a track." in data:
            self.res.append('None')
        if self.start2 and self.record:
            self.res.append(data.strip())
            self.record = False

        if self.start_2pi and self.record:
            if 'None designated' in data:
                self.res.append("None")
                self.res.append("None")
            elif 'Required' in data:
                pass
            else:
                self.res.append(data.strip())
        if self.start_pi and self.record:
            if data.strip():
                self.res.append(data.strip())
        if self.start_inst and self.record:
            if data.strip() and "Student Leaders" not in data:
                if self.i == 0:
                    self.tmp.append(data.strip())
                    self.i = 1
                elif self.i == 1:
                    self.tmp2.append(data.strip())
                    self.i = 0
            # print self.tmp, self.tmp2
        if self.start_leader:
            if "None designated" in data:
                self.res.append('None')
                self.res.append('None')
                self.start_leader = False
        if self.start_leader and self.record:
            if data.strip():
                if self.i == 0:
                    self.tmp.append(data.strip())
                    self.i = 1
                elif self.i == 1:
                    self.tmp2.append(data.strip())
                    self.i = 0
        if self.start_end:
            if "None designated" in data:
                self.res.append('None')
                self.res.append('None')
            elif data.strip():
                if self.i == 0:
                    self.tmp.append(data.strip())
                    self.i = 1
                elif self.i == 1:
                    self.tmp2.append(data.strip())
                    self.i = 0
        if self.start_advisor:
            if "None designated" in data:
                self.res.append('None')
                self.res.append('None')
            elif data.strip():
                if self.i == 0:
                    self.tmp.append(data.strip())
                    self.i = 1
                elif self.i == 1:
                    self.tmp2.append(data.strip())
                    self.i = 0
        if "Secondary PI" in data:
            self.start_2pi = True
            # print "start PI2"
        if "Primary PI" in data:
            self.start_pi = True
            # print "start PI"
        if "Instructors" in data:
            self.start_inst = True
            # print "start Instructors"
        if "Student Leaders" in data:
            # print "start Leaders"
            self.start_inst = False
            self.record = False
            self.start_leader = True
            if len(self.tmp) > 0:
                self.res.append(";".join(self.tmp))
                self.res.append(";".join(self.tmp2))
            else:
                self.res.append('None')
                self.res.append('None')
            self.tmp = []
            self.tmp2 = []
        if "Student Members" in data:
            # print "start Members"
            if self.start_leader:
                self.start_leader = False
                self.res.append(";".join(self.tmp))
                self.res.append(";".join(self.tmp2))
            self.record = False
            self.tmp = []
            self.tmp2 = []
            self.i = 0
            self.start_end = True
        if "Advisors" in data:
            # print "start Advisors"
            self.start_advisor = True
            self.tmp = []
            self.tmp2 = []
        if self.start_parts:
            try:
                d = data.strip().split(' to ')
                self.res.append(d[0])
                self.res.append(d[1])
            except:
                self.res.append('None')
                self.res.append('None')
            self.start_parts = False
        if "range of part numbers " in data:
            self.start_parts = True


class UserContribution(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
        self.date = False
        self.id = 0
        self.tmp = []
        self.res = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # if self.start:
        # print "Encountered a start tag:", tag
        # print attrs
        if tag == 'p':
            if 'id' in attrs:
                if attrs['id'] == "mw-sp-contributions-explain":
                    self.start = True
                    # print "START"

        if tag == 'li' and self.start:
            self.tmp = []
            self.date = True
            # print 'tmp', self.tmp

        if tag == 'a' and self.start and self.date:
            self.tmp.append(attrs['title'])
            # print 'tmp', self.tmp

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        if tag == 'li' and self.start:
            # print 'tmp', self.tmp
            self.res.append(self.tmp)
            # print 'res', self.tmp

        if tag == 'ul' and self.start:
            self.start = False

    def handle_data(self, data):
        # print "Encountered some data  :", data
        data = data.replace('\t ', ' ')
        data = data.replace('_-AND-_', '&')
        if self.date:
            date_object = datetime.strptime(data.strip(), '%H:%M, %d %B %Y')
            self.tmp.append(date_object.isoformat())
            self.date = False
            # print 'tmp', self.tmp


class UserContribution2015(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
        self.date = False
        self.id = 0
        self.tmp = []
        self.res = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # if self.start:
        # print "Encountered a start tag:", tag
        # print attrs
        if tag == 'ul':
            self.start = True
            # print "START"

        if tag == 'li' and self.start:
            self.tmp = []
            self.date = True
            # print 'tmp', self.tmp

        if tag == 'a' and self.start and self.date:
            self.tmp.append(attrs['title'])
            # print 'tmp', self.tmp

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        if tag == 'li' and self.start:
            # print 'tmp', self.tmp
            self.res.append(self.tmp)
            # print 'res', self.tmp

        if tag == 'ul' and self.start:
            self.start = False

    def handle_data(self, data):
        # print "Encountered some data  :", data
        data = data.replace('\t ', ' ')
        data = data.replace('_-AND-_', '&')
        if self.date:
            date_object = datetime.strptime(data.strip(), '%H:%M, %d %B %Y')
            self.tmp.append(date_object.isoformat())
            self.date = False
            # print 'tmp', self.tmp


class PageView(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
        self.date = False
        self.id = 0
        self.tmp = []
        self.res = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # if self.start:
        # print "Encountered a start tag:", tag
        # print attrs
        if tag == 'ol':
            if 'class' in attrs:
                if attrs['class'] == "special":
                    self.start = True
                    # print "START"

        if tag == 'li' and self.start:
            self.tmp = []

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        if tag == 'li' and self.start:
            self.res.append(self.tmp)
            self.tmp = []

        if tag == 'ol' and self.start:
            # print "OL STOP"
            self.start = False

    def handle_data(self, data):
        # print "Encountered some data  :", data
        data = data.strip()
        data = data.replace('\xe2\x80\x8e', '')
        data = data.replace('\xe2\x80\x8f ', '')
        data = data.replace('\t ', ' ')
        data = data.replace('_-AND-_', '&')

        if 'views' in data:
            data = data.replace('(', '')
            data = data.replace(',', '')
            data = data.replace(' views)', '')
        if data:
            self.tmp.append(data)


class PageContributions(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
        self.entry = False
        self.entry2 = False
        self.id = 0
        self.tmp = []
        self.res = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # if self.start:
        # print "Encountered a start tag:", tag
        # print attrs
        if tag == 'ul':
            if 'id' in attrs:
                if attrs['id'] == "pagehistory":
                    self.start = True
                    # print "START"

        if tag == 'li' and self.start:
            self.tmp = []
            # print 'tmp', self.tmp

        if tag == "input" and self.start:
            self.entry = True
        if tag == 'span':
            if 'class' in attrs:

                if tag == "span" and self.start and attrs['class'] == "mw-history-histlinks":
                    self.entry2 = True

                if tag == 'span' and self.start and self.entry:
                    if attrs['class'] == "mw-usertoollinks":
                        self.entry = False

                if tag == 'span' and self.start and attrs['class'] == "history-size":
                    self.entry = True

                if tag == 'span' and self.start and attrs['class'] == "history-user":
                    self.entry = True

                if tag == 'span' and self.start and attrs['class'] == "mw-usertoollinks":
                    self.entry = False

            # self.tmp.append(attrs['title'])
            # print 'tmp', self.tmp

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        if tag == 'li' and self.start:
            # print 'tmp', self.tmp
            self.res.append(self.tmp)
            # print 'res', self.tmp

        if tag == 'span' and self.entry:
            self.entry = False

        if tag == 'ul' and self.start:
            self.start = False

    def handle_data(self, data):
        # print "Encountered some data  :", data
        data = data.replace('\t ', ' ')

        if self.entry:
            data = data.strip()
            if data and data != '(cur | prev)':
                try:
                    date_object = datetime.strptime(data.strip(), '%H:%M, %d %B %Y')
                    self.tmp.append(date_object.isoformat())
                    self.entry2 = False
                except:
                    self.tmp.append(data)
            # self.entry = False
            # print 'tmp', self.tmp
        if self.entry2:
            data = data.strip()
            if data:
                try:
                    date_object = datetime.strptime(data.strip(), '%H:%M, %d %B %Y')
                    self.tmp.append(date_object.isoformat())
                except:
                    pass


class PageContributions2015(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
        self.entry = False
        self.id = 0
        self.tmp = []
        self.res = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # if self.start:
        # print "Encountered a start tag:", tag
        # print attrs
        if tag == 'ul':
            if 'id' in attrs:
                if attrs['id'] == "pagehistory":
                    self.start = True
                    # print "START"

        if tag == 'li' and self.start:
            self.tmp = []
            # print 'tmp', self.tmp

        if tag == "input" and self.start:
            self.entry = True

        if tag == 'span' and self.start and self.entry:
            if 'class' in attrs:
                if attrs['class'] == "mw-usertoollinks":
                    self.entry = False

        if tag == 'span' and self.start:
            if 'class' in attrs:
                if attrs['class'] == "history-size":
                    self.entry = True
        if 'class' in attrs:
            if tag == 'span' and self.start and attrs['class'] == "history-user":
                self.entry = True
            if tag == 'a' and self.start and attrs['class'] == "mw-changeslist-date":
                self.entry = True

            # self.tmp.append(attrs['title'])
            # print 'tmp', self.tmp

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        if tag == 'li' and self.start:
            # print 'tmp', self.tmp
            self.res.append(self.tmp)
            # print 'res', self.tmp

        if tag == 'span' and self.entry:
            self.entry = False

        if tag == 'ul' and self.start:
            self.start = False

    def handle_data(self, data):
        # print "Encountered some data  :", data
        data = data.replace('\t ', ' ')

        if self.entry:
            data = data.strip()
            if data:
                if data != "\xe2\x80\x8e":
                    try:
                        date_object = datetime.strptime(data.strip(), '%H:%M, %d %B %Y')
                        self.tmp.append(date_object.isoformat())
                    except:
                        self.tmp.append(data)
            # self.entry = False
            # print 'tmp', self.tmp


class Results(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.teambar = False
        self.resulticons = False
        self.championshipbar = False
        self.awardbar = False
        self.entry = False
        self.id = 0
        self.tmp = None
        self.res = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # if self.start:
        # print "Encountered a start tag:", tag
        # print attrs
        if tag == 'div':
            if 'class' in attrs:
                if attrs['class'] == "teambar":
                    self.teambar = True
                    if self.tmp is not None:
                        self.res.append(self.tmp)
                    self.tmp = {
                        "teamName": None,
                        "teamMedal": None,
                        "teamChampionship": 0,
                        "teamFinalist": 0,
                        "teamWinner": 0,
                        "teamAwards": []
                    }

        if tag == 'div':
            if 'class' in attrs:
                if attrs['class'] == "resulticons":
                    if not self.championshipbar:
                        self.resulticons = True

        if tag == 'div':
            if 'class' in attrs:
                if attrs['class'] == "championshipbar":
                    self.championshipbar = True
                    self.tmp['teamChampionship'] = 1

        if tag == 'div':
            if 'class' in attrs:
                if attrs['class'] == "awardbar":
                    self.awardbar = True

        if tag == 'img' and self.resulticons:
            if 'class' in attrs:
                if attrs['class'] == 'seal':
                    if attrs['src'] == 'http://igem.org/images/medals/seal_bronze.png':
                        self.tmp['teamMedal'] = 'bronze'
                    elif attrs['src'] == 'http://igem.org/images/medals/seal_silver.png':
                        self.tmp['teamMedal'] = 'silver'
                    elif attrs['src'] == 'http://igem.org/images/medals/seal_gold.png':
                        self.tmp['teamMedal'] = 'gold'
                    elif attrs['src'] == 'http://igem.org/images/medals/seal_blocked.png':
                        self.tmp['teamMedal'] = 'blocked'

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        if tag == 'div' and self.awardbar:
            self.awardbar = False

        if tag == 'div' and self.resulticons:
            self.resulticons = False

        if tag == 'div' and self.championshipbar:
            self.championshipbar = False

        if tag == 'a' and self.teambar:
            self.teambar = False

    def handle_data(self, data):
        # print "Encountered some data  :", data
        data = data.strip()
        data = data.replace('\t ', ' ')

        if self.teambar:
            self.tmp['teamName'] = data.replace(' ', '_')

        if self.awardbar:
            self.tmp['teamAwards'].append(data)
            if 'finalist' in data.lower():
                self.tmp['teamFinalist'] = 1
            if 'winner' in data.lower():
                self.tmp['teamWinner'] = 1


# instantiate the parser and fed it some HTML
# parser = MyHTMLParser()
# parser.feed('<html><head><title>Test</title></head>'
#             '<body><h1>Parse me!</h1></body></html>')
