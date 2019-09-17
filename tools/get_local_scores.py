from sklearn.neighbors import KDTree
import time 
import numpy as np 
import json 
from jsonslicer import JsonSlicer
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


citation = questions_answers_map('../data/cn_cn_citation_find.txt')
questions_dict = get_points('/media/data/ky/local/claims_questioon.json')
print('total {} have been tested'.format(len(questions_dict.keys())))
print('start  to load samples points')
ts = time.time()
#samples_dict = get_points('/media/data/ky/local/abs_test.json')
f = open('/media/data/ky/local/claims_test.json','r')
#objects = ijson.items(f, 'data.item')
#for obj in objects:
#    print(obj)

print(' had used {}'.format(time.time()-ts))
print('Start to calculate scores')
ts1 =time.time()
all_questions_scores = {}
for key in questions_dict.keys():
    pivots = questions_dict.get(key)
    question_score={}
    
   # for k in samples_dict.keys():
   #     s = samples_dict.get(k)
   #     s = np.asarray(s)
   #     score = get_scores(pivots,s)
   #     question_score[k] = score 
    for k,d in JsonSlicer(data,('data',None),path_mode='map_keys'):
        s = np.asarray(d)
        score = get_scores(pivots,s)
        question_score[k] = score 
    all_questions_scores[key] = question_score 
print('used {} to calculate scores'.format(time.time()-ts1))
with  open('./local/abs_socres.json','w') as j:
    json.dump(all_questions_scores,j,indent=4)



