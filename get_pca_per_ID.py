import csv
import jieba
import jieba.posseg as pseg
from bert_serving.client import BertClient
from sklearn.decomposition import PCA
import numpy as np
from sklearn.neighbors import KDTree



def get_contents(path,choice,*args):
    #*args = title\abs\claims\des
    #choice for question or answer
    with open(csv_path,'r') as csv_file:
        reader = csv.reader(csv_file,delimiter='\t')
        contents = {}
        ques_ans_map={}
        for row in reader:
            if ques_ans_map.get(row[0]):
                ques_ans_map.get(row[0]).append(row[5])
            else:
                ques_ans_map[row[0]]=[row[5]]
            if choice == 'answer':
                row = row[5:]
            else:
                row= row[:5]
            if contents.get(row[0]):
                continue
            else:
                content = []
                for arg in args:
                    if arg =='title':
                        content.append(row[1])
                        continue
                    elif arg == 'abs':
                        content.append(row[2])
                        continue
                    elif arg == 'claims':
                        content.append(row[3])
                        continue
                    elif arg == 'des':
                        content.append(row[4])
                        continue
                    else:
                        print('wrong input args')
                contents[row[0]] = content
        return contents,ques_ans_map


def stopwordlist(filepath):
    stopwords = [line.strip() for line in open(filepath,'r',encoding='utf-8')]
    return stopwords

def seg_sentence(sentence):
    sentence_seged = pseg.cut(sentence)
    stopwords = stopwordlist(stop_words_path)
    outstr = ''
    for word in sentence_seged:
        if word not in stopwords:
            if word!= '\t' and word.flag == 'n':
               outstr += word.word
               outstr += " "
    return list(set(outstr.split(' ')[:-1 ]))

def get_points(words):
    bc = BertClient()
    bert_vecs = bc.encode(words)
    pca = PCA(n_components=2, random_state=0)
    reduced_vecs = pca.fit_transform(bert_vecs)
    assert len(words)==len(reduced_vecs)
    return reduced_vecs


def get_closed_points(pivots,samples):
    X = samples
    tree = KDTree(X,leaf_size=10, metric='euclidean')
    score = 0
    for p in pivots:
        dist,ind = tree.query([p],k=1)
        score += dist
    return score/len(pivots)





if __name__ == '__main__':
    csv_path = './data/test1.csv'
    stop_words_path = '/home/ky/patent_search/CHN/stop_words1.txt'
    question_contents,ques_ans=get_contents(csv_path,'question','claims',)
    #ques_sample =question_contents.get('CN106030728A')[0]
    #words = seg_sentence(ques_sample)
    #pivots = get_points(words)
    print(ques_ans.get('CN102819268A'))

    answer_contents,_ = get_contents(csv_path,'answer','claims')
    #ans_sample = answer_contents.get('CN102427356A')[0]
    #ans_words = seg_sentence(ans_sample)
    #ans_points = get_points(ans_words)
    #print(get_closed_points(pivots,ans_points))
    question_id = 'CN102819268A'
    pivots =get_points(seg_sentence(question_contents.get(question_id)[0]))
    ans_ids = ques_ans.get(question_id)
    for ans in ans_ids:
        try:
            ans_samples=get_points(seg_sentence(answer_contents.get(ans)[0]))
            #print(ans_samples)
            score = get_closed_points(pivots,ans_samples)
        except:
            pass
            score = 'no content'
        print("answer {} , score {} ".format(ans,score))

    no_ans_id = 'CN103281954A'
    no_ans_ids = ques_ans.get(no_ans_id)
    for nans in no_ans_ids:
         try:
            ans_samples=get_points(seg_sentence(answer_contents.get(nans)[0]))
            score = get_closed_points(pivots,ans_samples)
         except:
            pass
            score = 'no content'
         print("not_answer {} , score {} ".format(nans,score))








