import os
import time
from os import walk
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import requests
import csv
import jieba
import jieba.posseg as pseg
from bert_serving.client import BertClient
from sklearn.decomposition import PCA
import numpy as np
from sklearn.neighbors import KDTree
from tqdm import tqdm
import json
import random



def stopwordlist(filepath):
    stopwords = [line.strip() for line in open(filepath,'r',encoding='utf-8')]
    return stopwords

def seg_sentence(sentence):
    sentence_seged = pseg.cut(sentence)
    stopwords = stopwordlist(stop_words_path)
    outstr = ''
    for word in sentence_seged:
        if word not in stopwords:
            if word!='\t' and word.flag == 'n':
                outstr += word.word
                outstr += " "
    return list(set(outstr.split(' ')[:-1]))

def get_points(words):
    bc = BertClient()
    bert_vecs = bc.encode(words)
    #pca = PCA(n_components=2, random_state=0)
    #reduced_vecs = pca.fit_transform(bert_vecs)
    #assert len(words) == len(reduced_vecs)
    #return reduced_vecs
    return bert_vecs

def get_closed_point(pivots,samples):
    tree = KDTree(samples, leaf_size=40, metric='euclidean')
    score = 0
    for p in pivots:
        dist,_ = tree.query([p], k=1)
        score += dist.item(0,0)
    return score/len(pivots)


def es_iterate_all_documents(es, index, pagesize=250, scroll_timeout="1m", **kwargs):
    """
    Helper to iterate ALL values from a single index
    Yields all the documents
    """
    is_first = True
    while True:
        if is_first:
            result = es.search(index=index, scroll='1m', **kwargs, body={"size": pagesize })
            is_first = False
        else:
            result = es.scroll(body={
                "scroll_id": scroll_id,
                "scroll": scroll_timeout
            })
        scroll_id = result["_scroll_id"]
        hits = result["hits"]["hits"]

        if not hits:
            break
        yield from(hit['_source'] for hit in hits)

def search_by_id(es,ID,part):
    result  = es.search(index='cpatentv4',body={'query':{'match':{'docid':ID}},"_source":[part]})
    part_result = result['hits']['hits'][0].get('_source').get(part)
    return part_result

if __name__ == '__main__':
    stop_words_path = '/home/ky/patent_search/CHN/stop_words.txt'
    es = Elasticsearch([{'host':'202.112.195.82','port':9200}])
    #question_id = 'CN106854453A'
    #question_return = es.search(index='cpatentv4',body={'query':{'match':{'docid':'CN101553679A'}},"_source":['abs']})
    #print( question_return['hits']['hits'][0].get('_source').get('abs'))
    #question_vecs = get_points(seg_sentence(question_abs))

    #with open('./data/cn_cn_citation_find.1.txt','r') as txt_file:
    with open('./data/100_2000_first10w.txt','r') as txt_file:
        question_answer_map = {}
        question_list =[]
        answer_list = []
        for line in txt_file:
            line = line.split()
            question_list.append(line[0])
            answer_list.append(line[1])
            if question_answer_map.get(line[0]):
                 question_answer_map.get(line[0]).append(line[1])
            else:
                question_answer_map[line[0]] = [line[1]]
    question_scores_map = {}
    qlist = list(set(question_list))
    for qid in qlist:
        qsentence = search_by_id(es,qid,'claims')

        q_points = get_points(seg_sentence(qsentence))
        real_aid = question_answer_map.get(qid)
        answer_scores_map = {}
        #with tqdm(total=len(set(answer_list))) as pbar:
        #answer_list_short = random.choices(answer_list,k=100)
        #test_list =list(set(question_answer_map.get(qid) + answer_list_short))
        #with tqdm(total=len(test_list)) as pbar:

        ans_id_list = question_answer_map.get(qid)
        #nanswer_list_short = [e for e in answer_list_short if e not in ans_id_list]

        print('____________{} test start:'.format(qid))
        with tqdm(total=len(question_answer_map.get(qid))) as pbar:
           for aid in question_answer_map.get(qid):
            try:
                asentence = search_by_id(es,aid,'claims')
                a_points = get_points(seg_sentence(asentence))
                score = get_closed_point(q_points,a_points)
                answer_scores_map[aid] = score
            except:
                pass
                answer_scores_map[aid] = 999999999
         #   pbar.update(1)
            pbar.update(1)
        question_scores_map[qid] = answer_scores_map
       # print('_______{} not answer_scores : '.format(qid))
       # for naid in nanswer_list_short:
       #      try:
       #         asentence = search_by_id(es,naid,'abs')
       #         a_points = get_points(seg_sentence(asentence))
       #         score = get_closed_point(q_points,a_points)
       #         answer_scores_map[aid] = score
       #         print(score)
       #      except:
       #         pass
       #         answer_scores_map[aid] = 999999999
         #

    with open('./data/result_claims.json','w') as fp:
        json.dump(question_scores_map,fp,indent = 4)



