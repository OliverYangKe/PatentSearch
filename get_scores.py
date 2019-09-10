from threading import Thread
from queue import Queue
import time
from elasticsearch import Elasticsearch
from tqdm import tqdm
import json
from pre_process_txt import stopwordlist, seg_sentence, get_points, get_closed_point, search_by_id
import logging
from time import time

#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger = logging.getLogger(__name__)


def question_samples(path):
    with open(path,'r') as data_file:
        question_samples={}
        for line in data_file:
            line = line.split()
            if question_samples.get(line[0]):
                question_samples.get(line[0]).append(line[1])
            else:
                question_samples[line[0]] = [line[1]]
    return question_samples


class BertDistanceCalculator(Thread):

    def __init__(self,queue,es,stopwords,part,questions_samples_map):
        Thread.__init__(self)
        self.queue = queue
        self.es = es
        self.stopwords = stopwords
        self.part = part
        self.questions_samples_map = questions_samples_map

    def run(self):
        while True:
            q_id,question_scores = self.queue.get()
            try:
                print(q_id)
                q_sentence = search_by_id(self.es,q_id,self.part)
                q_points = get_points(seg_sentence(q_sentence,self.stopwords))
                samples_id = self.questions_samples_map.get(q_id)
                samples_scores = {}
                for sample in samples_id:
                    try:
                        sample_sentence = search_by_id(self.es,sample,self.part)
                        sample_points = get_points(seg_sentence(sample_sentence,self.stopwords))
                        score = get_closed_point(q_points,sample_points)
                        samples_scores[sample] = score
                    except:
                        pass
                        samples_scores[sample] =9999
                question_scores[q_id]=samples_scores
            finally:
                self.queue.task_done()


def main():
    ts = time()
    stopwordspath = "./data/stopwords.txt"
    stopwords = stopwordlist(stopwordspath)
    es = Elasticsearch([{'host':'202.112.195.82','port':9200}])
    part = 'title'     #title, abs , claims, description
    questions_samples_map = question_samples('./data/100_2000_first10w.txt')
    question_scores={}
    queue = Queue()
    for x in range(8):
        worker = BertDistanceCalculator(queue,es,stopwords,part,questions_samples_map)
        worker.daemon = True
        worker.start()
    questions_id = questions_samples_map.keys()
    #with tqdm(total=len(questions_id)) as pbar:
    for q_id in questions_id:
 #           logger.debug('Queueing{}'.format(q_id))
            queue.put((q_id,question_scores))
            #pbar.update(1)
    queue.join()
   # logging.info('Took %s',time()-ts)
    print('Took %s',time() -ts)
    return question_scores


if __name__ == '__main__':
   question_scores=main()
   with open('./data/result_test','w') as fp:
       json.dump(question_scores,fp,indent=4)


