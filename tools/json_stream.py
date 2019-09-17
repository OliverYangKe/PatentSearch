from jsonslicer import JsonSlicer

with open('/media/data/ky/local/abs_question.json','r') as data:
    for k,d in JsonSlicer(data,('data',None),path_mode='map_keys'):
            print(k)
            print(len(d[0]))
