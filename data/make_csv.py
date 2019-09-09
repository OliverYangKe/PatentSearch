import csv

row = ['ID-cn1992','title-咖啡','abs-这是一杯手冲咖啡','cla-一定要用手','des-左手右手一个慢动作']

with open('./test.csv', 'w') as csv_f:
    writer = csv.writer(csv_f,delimiter='\t')
    writer.writerow(row)

