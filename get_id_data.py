from pre_prcess_txt import stopwordlist,seg_sentence,search_by_id
import argparse
from elasticsearch import Elasticsearch


def get_points(words,bc):
    bert_vecs = bc.encode(word)



def word_and_points(es,idq,ida,tag,sw):
    question_string = search_by_id(es,idq,tag)
    answer_string = search_by_id(es,ida,tag)
    questions_words = seg_sentence(question_string,sw)
    answer_words =  seg_sentence(answer_string,sw)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("question_id",help="docid for question")
    parser.add_argument("answer_id",help="docid for answer")
    parser.add_argument("part",help="which part from doc",\
                        choices=["abs","claims","descriptions"])

    args = parser.parse_args()

    stopwords = stopwordlist("./data/stopwords.txt")
    es = Elasticsearch([{'host':'202.112.195.82','port':9200}])




