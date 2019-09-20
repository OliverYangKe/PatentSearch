import jieba.posseg as pseg
from bert_serving.client import BertClient
from sklearn.neighbors import KDTree



def stopwordlist(filepath):
    stopwords = [line.strip() for line in open(filepath,'r',encoding='utf-8')]
    return stopwords

def seg_sentence(sentence,stopwords):
    sentence_seged = pseg.cut(sentence)
    outstr = ''
    for word in sentence_seged:
        if word not in stopwords:
            if word!='\t' and (word.flag == 'n' or word.flag == 'v'):
                outstr += word.word
                outstr += " "
    return list(set(outstr.split(' ')[:-1]))

def get_points(words):
    """
    https://github.com/hanxiao/bert-as-service
    bert-serving-start -model_dir /home/ky/bert/chinese_L-12_H-768_A-12/ -num_worker=4
    """
    bc = BertClient()
    bert_vecs = bc.encode(words)
    return bert_vecs

def get_closed_point(pivots,samples):
    tree = KDTree(samples, leaf_size=40, metric='euclidean')
    score = 0
    for p in pivots:
        dist,_ = tree.query([p], k=1)
        score += dist.item(0,0)

    return score/len(pivots)


#def es_iterate_all_documents(es, index, pagesize=250, scroll_timeout="1m", **kwargs):
#    """
#    Helper to iterate ALL values from a single index
#    Yields all the documents
#    """
#    is_first = True
#    while True:
#        if is_first:
#            result = es.search(index=index, scroll='1m', **kwargs, body={"size": pagesize })
#            is_first = False
#        else:
#            result = es.scroll(body={
#                "scroll_id": scroll_id,
#                "scroll": scroll_timeout
#            })
#        scroll_id = result["_scroll_id"]
#        hits = result["hits"]["hits"]

#        if not hits:
#            break
#        yield from(hit['_source'] for hit in hits)

def search_by_id(es,ID,part):
    result  = es.search(index='cpatentv4',body={'query':{'match':{'docid':ID}},"_source":[part]})
    part_result = result['hits']['hits'][0].get('_source').get(part)
    return part_result


