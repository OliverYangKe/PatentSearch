import pickle 


with open('./data/sample.txt','rb') as f:
     alist =pickle.load(f)
     print(alist)
