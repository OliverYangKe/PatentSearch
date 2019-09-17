import sys
sys.path.insert(1,'../')
from pre_process_txt import stopwordlist, seg_sentence, get_points, search_by_id
from get_scores import question_samples
import logging
import os
from functools import partial
from multiprocessing.pool import Pool
from time import time
from elasticsearch import Elasticsearch
import json
from threading import Thread
from queue import Queue
import csv
def get_points_by_id(es,part,stopwords,ID):
    sentence = search_by_id(es,ID,part)
    try:
        points = get_points(seg_sentence(sentence,stopwords))
        points = points.tolist()
        return points
    except:
        pass
        print('fail')
        return None

def get_id(path,qa):
    with open(path,'r') as data_file:
        id_list=[]
        for line in data_file:
            line = line.split()
            if qa == 'question':
                id_list.append(line[0])
            else :
                id_list.append(line[1])
    return list(set(id_list))

class PointsToLocal(Thread):
    def __init__(self,queue,es,part,stopwords):
        Thread.__init__(self)
        self.queue = queue
        self.es = es
        self.stopwords = stopwords
        self.part = part
        #self.ID = ID
    def run(self):
        while True:
            ID,all_id_points__map = self.queue.get()
            try:
              points_id= get_points_by_id(self.es,self.part,self.stopwords,ID)
              all_id_points__map[ID]=points_id
            except:
              pass
              print('aaaaaaaaaaaaaaa')
            finally:
                self.queue.task_done()

def main():
    ts = time()
    stopwordspath = '../data/stopwords.txt'
    stopwords = stopwordlist(stopwordspath)
    es = Elasticsearch([{'host':'202.112.195.82','port':9200}])
    question_list = get_id('../data/100_2000_first10w.txt','question')
    test_list = get_id('../data/100_2000_first10w.txt','test')
    part = 'abs'
    qa = 'test'
    #points_to_local = partial(get_points_by_id,(es,part,stopwords,f))
    #with Pool(8) as p:
       # print(points_to_local)
    #    p.map(points_to_local,question_list)
    #logging.info('Tool %s seconds', time() -ts)
    #f.close()
    queue = Queue()
    for x in range(100):
        worker = PointsToLocal(queue,es,part,stopwords)
        worker.daemon = True
        worker.start()
    all_id_points__map={}
    # change list
    for ID in test_list:
        queue.put((ID,all_id_points__map))
    queue.join()
    return all_id_points__map


if __name__ == '__main__':
    a = main()
    with open('/media/data/ky/local/abs_test_1.json','w') as fp:
        json.dump(a,fp)


