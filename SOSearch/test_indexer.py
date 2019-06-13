from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from os import listdir
import os
import xml.etree.ElementTree as ET
import sqlite3
import configparser
import string
from bs4 import BeautifulSoup

class Doc:
    docid = 0
    tf = 0
    dl = 0
    def __init__(self, docid, tf, dl, extra_fields=[]):
        self.docid = docid
        self.tf = tf
        self.dl = dl
        self.extra_fields = extra_fields
    def __repr__(self):
        # return str({'id':self.docid, 'tf':self.tf, 'dl':self.dl})
        # return(str(self.docid)  + '\t' + str(self.tf) + '\t' + str(self.dl))
        base_str = "{}\t{}\t{}".format(self.docid, self.tf, self.dl)
        for extra_field in self.extra_fields:
            base_str  += "\t{}".format(extra_field)
        return base_str
    def __str__(self):
        # return str({'id':self.docid, 'tf':self.tf, 'dl':self.dl})
        # return(str(self.docid) + '\t' + str(self.tf) + '\t' + str(self.dl))
        return self.__repr__()

class IndexModule:
    stop_words = set()
    postings_lists = {}
    
    def __init__(self, table_name, db_path):
        self.stop_words = stopwords.words('english') + list(string.punctuation)
        self.file_path = table_name
        self.db_path = db_path
        self.table_name = table_name
        self.count = 0
        self.avg_dl = 0
        if os.path.exists(self.file_path):
            f = open(self.file_path, 'r')
            content = eval(f.read())
            # self.postings_lists = content['index']
            self.count = content['count']
            self.avg_dl = content['avg_dl']
            f.close()

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    def get_terms(self, text):
        text = BeautifulSoup(text, 'lxml').text
        tokens = word_tokenize(text.lower())

        dl = len(tokens)
        tokens = [i for i in tokens if (i not in self.stop_words and not self.is_number(i))]
        porter = PorterStemmer()
        tokens = [porter.stem(i) for i in tokens]
        terms = {}
        for t in tokens:
            terms[t] = terms.get(t, 0)+1
        return dl, terms

    def update(self, docs, extra_field_keys=[]):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        dl_total = self.count*self.avg_dl
        for d in docs:
            text = d['text']
            extra_fields = []
            for extra_field_key in extra_field_keys:
                extra_fields.append(d[extra_field_key])
            dl, terms = self.get_terms(text)
            dl_total += dl
            if dl==0: continue
            self.count += 1
            for key, value in terms.items():
                doc = Doc(d['id'], value, dl, extra_fields)
                c.execute('SELECT * FROM {} WHERE term=?'.format(self.table_name), (key,))
                r = c.fetchone()
                if r is None:
                    t = (key, 1, str(doc))
                    c.execute("INSERT INTO {} VALUES (?, ?, ?)".format(self.table_name), t)
                else:
                    t = (r[1]+1, r[2]+'\n'+str(doc), key)
                    c.execute("UPDATE {} SET df=?,docs=? WHERE term=?".format(self.table_name), t)

            # tag index
            if self.table_name == 'question_index':
                tags = d['tags'].split(',')
                tagdoc = Doc(d['id'], 1, dl, extra_fields)
                for tag in tags:
                    c.execute('SELECT * FROM tag_index WHERE tag=?', (tag,))
                    r = c.fetchone()
                    if r is None:
                        t = (tag, 1, str(doc))
                        c.execute("INSERT INTO tag_index VALUES (?, ?, ?)", t)
                    else:
                        t = (r[1] + 1, r[2] + '\n' + str(doc), tag)
                        c.execute("UPDATE tag_index SET df=?,docs=? WHERE tag=?", t)

        self.avg_dl = dl_total/self.count
        content = {'count': self.count, 'avg_dl': self.avg_dl}
        with open(self.file_path, 'w') as f:
            f.write(str(content))
        conn.commit()
        conn.close()
            # print(content)



if __name__ == "__main__":
    conn = sqlite3.connect('test_db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM question_index where term=?', ('python',))
    r=c.fetchone()
    while (r is not None):
        # if (r[0]!='python'): continue
        print(r[0],r[1])
        print(r[2])
        r = c.fetchone()
    # im = IndexModule('Question_index.txt')
    # print(im.count) 
    # print(im.avg_dl)
    # cnt = 0
    # for term in im.postings_lists:
    #     cnt += 1
    # print('term nubmer', cnt)
    # test_list = im.postings_lists['python']
    # print('length of doc list', test_list[0])
    # print('first item of doc list', test_list[1][0])
        # print(term)
        # print(im.postings_lists[term])


