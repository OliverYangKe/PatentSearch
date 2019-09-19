from sklearn.neighbors import KDTree
import time 
import numpy as np 
import json 
from jsonslicer import JsonSlicer
from tqdm import tqdm 
from threading import Thread 
from queue import Queue 


def get_points(path):
    with open(path,'r') as f:
        points_dict = json.load(f)
    return points_dict


def get_scores(pivots,samples):
    tree = KDTree(samples, leaf_size=40, metric='euclidean')
    score = 0
    for p in pivots:
        dist,_ = tree.query([p], k=1)
        score += dist.item(0,0)

    return score/len(pivots)

def questions_answers_map(path):
    questions_answers_map = {}
    with open(path,'r') as f:
        for line in f:
            line = line.split()
            if questions_answers_map.get(line[0]):
                questions_answers_map.get(line[0]).append(line[1])
            else:
                questions_answers_map[line[0]] = [line[1]]
    return questions_answers_map

class ScoreCalculator(Thread):
    
    def __init__(self,queue,questions_dict,f):
        Thread.__init__(self)
        self.queue = queue 
        self.questions_dict=questions_dict 
        self.f = f
 
    
    def score(self):
        key,all_questions_scores = self.queue.get()
        pivots = self.questions_dict.get(key)
        question_score={}
        p = np.asarray(pivots)  
        tree = KDTree(p, leaf_size=40, metric='euclidean')
        flag = None 
        value = 0
        n = 0
        for s in JsonSlicer(self.f,(None,None),path_mode='full'):
            print(s)
            if flag == None or s[0]!= flag:
                if flag == None:
                    flag = s[0]
                    z = np.asarray(s[2])
                    dist,_ = tree.query([z], k=1)
                    value += dist.item(0,0)
                    n += 1
                else:
                    question_score[flag]=value/n
                    flag = s[0]
                    value = 0
                    n = 0
                    dist,_ = tree.query([z], k=1)
                    value += dist.item(0,0)
                    n += 1


            else:
                z = np.asarray(s[2])
                dist,_ = tree.query([z], k=1)
                value += dist.item(0,0)
                n+=1
        question_score[flag] = value/n
        all_questions_scores[key] = question_score

    def run(self):
        while True:
            try:
                self.score()
            finally:
                self.queue.task_done()


def main():
    questions_dict = get_points('/media/data/ky/local/claims_questioon.json')
    all_questions_scores = {}
    f = open('/media/data/ky/local/claims_test.json','r')
    queue = Queue()
    for x in range(48):
        worker = ScoreCalculator(queue,questions_dict,f)
        worker.daemon = True
        worker.start()
    
    for key in questions_dict.keys():
        queue.put((key,all_questions_scores))
    queue.join()
    return all_questions_scores 

if __name__ == '__main__':
    a = main()
    with  open('./local/claims_scores.json','w') as j:
        json.dump(a,j,indent=4)



