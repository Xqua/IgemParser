from HTMLParser import HTMLParser

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
        if self.start:
            print "Encountered a start tag:", tag
            print attrs
        if tag == 'table':
            if 'id' in attrs:
                if attrs['id'] == "mw-prefixindex-list-table":
                    self.start = True
                    print "START"

        if tag == 'a' and self.start:
            self.res.append(attrs['title'])
            print 'tmp', self.res

    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag
        if tag == 'table' and self.start:
            self.start = False

    def handle_data(self, data):
        print "Encountered some data  :", data


class TeamPage(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
        self.start2 = False
        self.start_end = False
        self.start_pi = False
        self.start_2pi = False
        self.start_inst = False
        self.record = False
        self.id = 0
        self.tmp = []
        self.tmp2 = []
        self.res = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # if self.start:
        # print "Encountered a start tag:", tag
        # print attrs

        if tag == 'table':
            if 'id' in attrs:
                if attrs['id'] == "table_info":
                    self.start = True
                    print "START"
        if tag == 'table':
            if 'id' in attrs:
                if attrs['id'] == "table_abstract":
                    self.start2 = True
                    print "START2"

        if tag == 'tr' and self.start:
            self.record = True

        if tag == 'td' and self.start2:
            self.record = True

        if tag == 'a' and self.start_pi:
            self.record = True
        if tag == 'TD' and self.start_pi:
            if attrs['style'] == "width:200px":
                self.record = True

    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag
        if tag == 'table' and self.start:
            self.start = False
        if tag == 'table' and self.start2:
            self.start2 = False
            # self.res.append(self.tmp)
            # print 'res', self.res
        if self.start_pi or self.start_2pi and tag == 'tr':
            self.start_pi = False
            self.start_2pi = False

    def handle_data(self, data):
        print "Encountered some data  :", data
        if self.start and self.record:
            if ':' not in data:
                self.res.append(data)
                self.record = False
        if "Assigned Track" in data:
            self.res.append(data.strip().split(':')[1])
        if self.start2 and self.record:
            self.res.append(data.strip())
            self.record = False
        if "Secondary PI" in data:
            self.start_2pi = True
        if "Primary PI" in data:
            self.start_pi = True
        if "Instructors" in data:
            self.start_inst = True
        if "Student Members" in data:
            self.start_end = True
        if self.start_pi and self.record:
            self.res.append(data)
            self.record = False


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
        if self.start:
            print "Encountered a start tag:", tag
            print attrs
        if tag == 'p':
            if 'id' in attrs:
                if attrs['id'] == "mw-sp-contributions-explain":
                    self.start = True
                    print "START"

        if tag == 'li' and self.start:
            self.tmp = []
            self.date = True
            print 'tmp', self.tmp

        if tag == 'a' and self.start and self.date:
            self.tmp.append(attrs['title'])
            print 'tmp', self.tmp

    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag
        if tag == 'li' and self.start:
            print 'tmp', self.tmp
            self.res.append(self.tmp)
            print 'res', self.tmp

        if tag == 'ul' and self.start:
            self.start = False

    def handle_data(self, data):
        print "Encountered some data  :", data
        if self.date:
            self.tmp.append(data)
            self.date = False
            print 'tmp', self.tmp


class PageContributions(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
        self.entry = False
        self.id = 0
        self.tmp = []
        self.res = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.start:
            print "Encountered a start tag:", tag
            print attrs
        if tag == 'ul':
            if 'id' in attrs:
                if attrs['id'] == "pagehistory":
                    self.start = True
                    print "START"

        if tag == 'li' and self.start:
            self.tmp = []
            print 'tmp', self.tmp

        if tag == "input" and self.start:
            self.entry = True

        if tag == 'span' and self.start and self.entry:
            if attrs['class'] == "mw-usertoollinks":
                self.entry = False

        if tag == 'span' and self.start and attrs['class'] == "history-size":
            self.entry = True

            # self.tmp.append(attrs['title'])
            # print 'tmp', self.tmp

    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag
        if tag == 'li' and self.start:
            print 'tmp', self.tmp
            self.res.append(self.tmp)
            print 'res', self.tmp

        if tag == 'span' and self.entry:
            self.entry = False

        if tag == 'ul' and self.start:
            self.start = False

    def handle_data(self, data):
        print "Encountered some data  :", data
        if self.entry:
            data = data.strip()
            if data:
                self.tmp.append(data)
            # self.entry = False
            print 'tmp', self.tmp


# instantiate the parser and fed it some HTML
# parser = MyHTMLParser()
# parser.feed('<html><head><title>Test</title></head>'
#             '<body><h1>Parse me!</h1></body></html>')
