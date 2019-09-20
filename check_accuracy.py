import json
import operator


with open('./data/cn_cn_citation_find.txt','r') as standard_result:
     question_answer_map = {}

     for line in standard_result:
         line = line.split()
         if question_answer_map.get(line[0]):
             question_answer_map.get(line[0]).append(line[1])
         else:
             question_answer_map[line[0]] = [line[1]]


print(set(question_answer_map.get('CN102025838A')))
json_file = open('./tools/local/abs_socres.json','r')
json_data = json.load(json_file)

test_keys = json_data.keys()
#test_result=json_data.get('CN105239086A')
#sorted_result = sorted(test_result.items(), key=operator.itemgetter(1))
#print(sorted_result[0][0])
point = 0
for key in json_data.keys():
    result = json_data.get(key)
    sorted_result = sorted(result.items(), key=operator.itemgetter(1))
 #   print(sorted_result[1][0])
    answer_list = question_answer_map.get(key)
    for i in range(100):
        if sorted_result[i][0] in answer_list:
            point += 1
            break

print(len(test_keys))
print('-------the accuracy is {}'.format(point/(len(test_keys)*0.78)))


