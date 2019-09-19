from jsonslicer import JsonSlicer

with open('/media/data/ky/local/claims_test.json','r') as data:
    for k in JsonSlicer(data,('CN105019422A',None),path_mode='full'):
        print(len(k))
