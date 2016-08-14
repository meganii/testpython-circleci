# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import cosine_similarity

import csv
import MeCab
import re
import yaml

from collections import OrderedDict, defaultdict

def mecabAnalyzer(doc, to_stem=True):
    p = re.compile(r'<.*?>')
    tagger = MeCab.Tagger('mecabrc')  # 別のTaggerを使ってもいい
    mecab_result = tagger.parse(p.sub("",doc))
    # mecab_result = tagger.parse(doc)
    info_of_words = mecab_result.split('\n')
    words = []
    for info in info_of_words:
        # macabで分けると、文の最後に’’が、その手前に'EOS'が来る
        if info == 'EOS' or info == '':
            break
            # info => 'な\t助詞,終助詞,*,*,*,*,な,ナ,ナ'
        info_elems = info.split(',')
        # 6番目に、無活用系の単語が入る。もし6番目が'*'だったら0番目を入れる
        if info_elems[6] == '*':
            # info_elems[0] => 'ヴァンロッサム\t名詞'
            words.append(info_elems[0][:-3])
            continue
        if to_stem:
            # 語幹に変換
            words.append(info_elems[6])
            continue
        # 語をそのまま
        words.append(info_elems[0][:-3])
    return words

def tf(doc):
    vectorizer = CountVectorizer(analyzer=mecabAnalyzer,token_pattern=u'(?u)\\b\\w+\\b')
    features = vectorizer.fit_transform(doc)
    terms = vectorizer.get_feature_names()
    return features, terms

def tfidf(docs):
    vectorizer = TfidfVectorizer(analyzer=mecabAnalyzer ,min_df=1, max_df=50, token_pattern=u'(?u)\\b\\w+\\b')
    features = vectorizer.fit_transform(docs)
    terms = vectorizer.get_feature_names()
    return features, terms

def getDocsList(filepath):
    f = open(filepath, 'r')
    lines = f.readlines()
    return [re.sub(r"[0-9].+?|\/|\"|\(|\)","",l) for l in lines]

def getFileList(filepath):
    f = open(filepath, 'r')
    lines = f.readlines()
    return [l.replace('\n','').split('\t') for l in lines]

def getRelatedPosts(docs, tfidf_mtx):
    '''
    それぞれのドキュメントに類似するドキュメントの２次元配列を返す。
    [
     [docNo, docNo],
     []
     ...
    '''
    cos_table = []
    for index in range(0, len(docs)):
        s = defaultdict(int)
        for i, tfidf in enumerate(tfidf_mtx):
            if i == index:
                s[i] = 0
                continue
            cos = cosine_similarity(tfidf_mtx[index].reshape(1, -1), tfidf.reshape(1, -1))
            s[i] = cos
        top_cos = sorted(s.items(), key=lambda t:t[1], reverse=True)
        top_cos = filter(lambda t:t[1] > 0.05, top_cos)
        cos_table.append(list(top_cos))
    return cos_table

if __name__ == '__main__':
    filelist = getFileList('tmp/filenamelist.txt')
    docs = getDocsList('tmp/contents.txt')

    features, terms = tfidf(docs)
    tfidf_mtx = features.toarray()

    relatedposts = getRelatedPosts(docs, tfidf_mtx)

    yaml = open('data/relatedposts.yml','w')
    yaml.write('Url:\n')
    for i, posts in enumerate(relatedposts):
        yaml.write('  ')
        yaml.write(filelist[i][0])
        yaml.write(':\n')
        cnt = 1
        for k, v in posts:
            yaml.write("    post{0}:\n".format(cnt))
            yaml.write("      title: {0}\n".format(filelist[k][2]))
            yaml.write("      link: {0}\n".format(filelist[k][1]))
            cnt += 1
    yaml.close()
