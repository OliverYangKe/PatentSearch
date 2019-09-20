from  pre_process_txt import stopwordlist,seg_sentence,get_points,get_closed_point,search_by_id 
from elasticsearch import Elasticsearch
from sklearn.neighbors import KDTree 
from time import time 
import operator 

class ScoreCaculator():
    def __init__(self,qid,tidlist,partlist,es):
        self.qid = qid
        self.tidlist = tidlist 
        self.partlist =partlist
        self.es = es 

    def get_vecs(self,ID,part):
        string = search_by_id(self.es,ID,part)
        words = seg_sentence(string,stopwords)
        bert_vecs = get_points(words)
        return bert_vecs


    def score_calculator(self):
        scores={}
        for tid in self.tidlist:
            score=0
            try:
                for part in self.partlist.split(','):
                    pivots =self.get_vecs(self.qid,part)
                    samples = self.get_vecs(tid,part)
                    tree = KDTree(samples,leaf_size=40,metric='euclidean')
                    for p in pivots:
                        dist,_ = tree.query([p], k=1)
                        if part == 'title':
                            score +=  dist.item(0,0)
                        elif part == 'abs':
                            score+= 2*dist.item(0,0)
                        elif part == 'claims' :
                            score += 3*dist.item(0,0)
                        elif part == 'description':
                            score += 4*dist.item(0,0)
                        else:
                            print('wrong part')
            except:
                pass
                print('can not find this doc')
                continue
            scores[tid]=score/len(pivots)
            
        
        #return {qid:scores}
        return scores 


if __name__=='__main__':

        es = Elasticsearch([{'host':'202.112.195.82','port':9200}]) 
        stopwords = stopwordlist("./data/stopwords.txt")
        qid = 'CN102025838A'
        tidlist = []
        with open('./data/100_2000_first10w.txt','r') as data:
        
            for line in data:
                line = line.split('\t')
                if line[0] == qid:
                    tidlist.append(line[1].rstrip('\n'))
                if len(tidlist) == 100:
                    break
        aidlist = ['CN101521861A', 'CN101267597A', 'CN101026652A']        
        for aid in aidlist :
            if aid not in tidlist:
                tidlist.append(aid)
        
        

        partlist = 'title,abs,claims,description'
        ts=time()
        sc = ScoreCaculator(qid,tidlist,partlist,es)
        s =sc.score_calculator()
        sorted_s =sorted(s,key=s.get)
        print('we used {}'.format(time()-ts))
        for aid in aidlist:
            if aid in sorted_s:
                print(aid)
                print(sorted_s.index(aid))
