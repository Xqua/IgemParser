#!/usr/bin/python
# -*- coding: utf8 -*-

import pandas as pd
import numpy as np
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize
from nltk.corpus import wordnet
from progressbar import Bar, ETA, Percentage, ProgressBar, Timer, Counter
from scipy import stats
import re

import sys
reload(sys)
sys.setdefaultencoding('utf8')


def is_noun(tag):
    return tag in ['NN', 'NNS', 'NNP', 'NNPS']


def is_verb(tag):
    return tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']


def is_adverb(tag):
    return tag in ['RB', 'RBR', 'RBS']


def is_adjective(tag):
    return tag in ['JJ', 'JJR', 'JJS']


def penn_to_wn(tag):
    if is_adjective(tag):
        return wn.ADJ
    elif is_noun(tag):
        return wn.NOUN
    elif is_adverb(tag):
        return wn.ADV
    elif is_verb(tag):
        return wn.VERB
    return None


def remove_dot(text):
    if text[-1] == '.':
        return text[:-1]
    else:
        return text


def in_wordnet(word):
    return True if word in all_lemmas else False


def cleanHTMLtags(text):
    p = re.compile("<[^>]*>")
    text = p.sub(' ', text)
    return text

df = pd.read_csv('results/team_pages_text_db.tsv', sep='\t')

lemmatizer = nltk.stem.WordNetLemmatizer()
all_lemmas = []
words = open('/usr/share/dict/words').readlines()
words = [i.strip() for i in words]
for w in words:
    all_lemmas.append(w)
words = set(words)
for syn in wordnet.all_synsets():
    for i in syn.lemma_names():
        if i not in words:
            all_lemmas.append(i)
all_lemmas = set(all_lemmas)

ngram_db = open('results/team_pages_1gram_db.tsv', 'w')
ngram_db.write('Year\tTeamID\tPage\tWord\tCount\tPage_Frequency\n')
stats_db = open('results/team_pages_text_stats_db.tsv', 'w')
stats_db.write('Year\tTeamID\tPage\tUniqueWordCount\tSentencesCount\tEntropy\n')
clean_text_db = open('results/clean_text_db.xml', 'w')
clean_text_db.write('<clean_text_db>\n')
page2id = open('results/page2pageID.tsv', 'w')
page2id.write('Page\tPageID\tGood\n')
tpid = {}
# ProgressBar(, maxval=300)
bar = ProgressBar(widgets=['NLPing ,,, Done:', Counter(), '/', str(len(df)), Percentage(), Bar(), ETA(), '  ', Timer()])
for i in bar(range(len(df))):
    y = df['Year'][i]
    tID = df['TeamID'][i]
    page = df['Page'][i]
    if y not in tpid:
        tpid[y] = {}
    if tID not in tpid[y]:
        tpid[y][tID] = 0
    pid = str(tID) + '_' + str(tpid[y][tID])
    tpid[y][tID] += 1
    try:
        text = open(df['Path'][i]).read()
        text = cleanHTMLtags(text)
        text = text.replace('"', '')
        text = text.replace('>', '')
        text = text.replace('<', '')
        text = text.replace('/', ' ')
        sentences = []
        for line in text.split('\n'):
            sent_tokenize_list = sent_tokenize(line)
            sentences += [remove_dot(i) for i in sent_tokenize_list]
        tokens = []
        for sentence in sentences:
            tokens.append(nltk.tokenize.word_tokenize(sentence))
        tokens = [i for i in tokens if i]
        out = ""
        for sentence in tokens:
            out += ' '.join(sentence) + '\n'
        out = out.replace('&', ' and ')
        out = out.replace('<', '')
        out = out.replace('>', '')
        POS = []
        for sentence in tokens:
            POS.append(nltk.pos_tag(sentence))
        lemmed = []
        to_ngram = []
        out_lem = ""
        for sentence in POS:
            tmp = []
            for word, pos in sentence:
                word = word.replace('"', '')
                word = word.decode('utf8')
                word = unicode(word).replace(u'“', '')
                poswn = penn_to_wn(pos)
                if poswn:
                    lem = lemmatizer.lemmatize(word, pos=poswn)
                else:
                    lem = lemmatizer.lemmatize(word)

                # print word, pos
                tmp.append(lem)
                if lem[-1] == '.':
                    lem = lem[:-1]
                if in_wordnet(lem):
                    lem = lem.replace("'s", '')
                    if lem not in ["'s", "u"]:
                        try:
                            float(lem)
                            number = True
                        except:
                            number = False
                        if not number:
                            if lem.strip():
                                to_ngram.append(lem.lower())
            lemmed.append(tmp)
            out_lem += ' '.join(tmp) + '\n'
        out_lem = out_lem.replace('&', ' and ')
        out_lem = out_lem.replace('<', '')
        out_lem = out_lem.replace('>', '')
        clean_text_db.write('<Entry>\n\t<Year>%s</Year>\n\t<PageID>%s</PageID>\n\t<TeamID>%s</TeamID>\n\t<Text>%s</Text>\n\t<Lemma>%s</Lemma>\n</Entry>\n' % (y, pid, tID, out, out_lem))
        unique = np.unique(to_ngram)
        counts = []
        freq = []
        for i in unique:
            c = to_ngram.count(i)
            counts.append(c)
        tot = float(np.sum(counts))
        for i in counts:
            freq.append(i / tot)
        for i in range(len(unique)):
            out = [str(i) for i in [y, tID, pid, unique[i], counts[i], freq[i]]]
            ngram_db.write('\t'.join(out) + '\n')
        stat = [str(i) for i in [y, tID, pid, len(unique), len(lemmed), stats.entropy(np.array(counts) / tot)]]
        stats_db.write('\t'.join(stat) + '\n')
        page2id.write('%s\t%s\t1\n' % (page, pid))
    except KeyboardInterrupt:
        break
    except:
        #     print e
        page2id.write('%s\t%s\t0\n' % (page, pid))
        #     # print "Well ... that's life"
        #     # print text
        #     pass
