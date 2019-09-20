from pre_process_txt import stopwordlist,seg_sentence,search_by_id
import argparse
from elasticsearch import Elasticsearch
from sklearn.decomposition import PCA
from bert_serving.client import BertClient 
import pickle 



def get_points(words,bc):
    bert_vecs = bc.encode(words)
    #pca =PCA(n_components=2,random_state=None)
    #array=pca.fit_transform(bert_vecs)
    #X = []
    #Y = []
    #for i in array:
    #    X.append(float(i[0]))
    #    Y.append(float(i[1]))

    return bert_vecs 


def word_and_points(es,tag,sw,bc,idlist):
    i=0
    k = []
    v = []
    for ID in idlist.split(','):
        print(ID)
        string = search_by_id(es,ID,tag)
        words = seg_sentence(string,sw)
        v = v +get_points(words,bc).tolist()
        k = k +[w+'__'+str(i) for w in words]
        i+=1
    pca = PCA(n_components=2,random_state=None)
    array = pca.fit_transform(v)
    print(k)
    print(len(k))
    print(len(array))
    return [k,array]


 #   question_string = search_by_id(es,idq,tag)
 #   questions_words = seg_sentence(question_string,sw)
 #   answer_words =  seg_sentence(answer_string,sw)
 #   question_set = get_points(questions_words,bc)
 #   answer_set = get_points(answer_words,bc)
 #   return question_set,answer_set 



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l",'--list',help="delimited list ,docids for documents",type=str)
    #parser.add_argument("--answer_id",help="docid for answer")
    parser.add_argument("--part",help="which part from doc",\
                        choices=["title","abs","claims","description"])

    args = parser.parse_args()
    bc = BertClient()
    stopwords = stopwordlist("./data/stopwords.txt")
    es = Elasticsearch([{'host':'202.112.195.82','port':9200}])
    l = word_and_points(es,args.part,stopwords,bc,args.list)
    with open('./data/sample.txt','wb') as f:
        pickle.dump(l,f)
        


