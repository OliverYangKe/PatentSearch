# PatentSearch
 This project aims to search similiary patent documents when a new patent is uploaded.
 

#Bert-embeding provided by Dr.hanxiao   https://github.com/hanxiao/bert-as-service 

install

pip install bert-serving-server  # server
pip install bert-serving-client  # client, independent of `bert-serving-server`



start server

bert-serving-start -model_dir /tmp/chinese_L-12_H-768_A-12/ -num_worker=4 

virtual env

$ pip install -r requirements.txt

run the code :

python get_score.py


