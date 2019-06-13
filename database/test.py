import time
import json
import os

time_sample = '2018-02-18 09:14:53Z'
parsed_time = time.strptime(time_sample, "%Y-%m-%d %H:%M:%Sz")
print(parsed_time)

time_sample2 = "Jun 6 at 14:38"
parsed_time2 = time.strptime(time_sample2, "%b %d at %H:%M")
this_year = time.strptime('2019', '%Y')
new_time = time.struct_time(this_year[:1] + parsed_time2[1:])
print(time.strftime("%Y-%m-%d %H:%M:%SZ", new_time))

sample_file_path = './data/sample_mid_question_answer.json'
json_file = json.load(open(sample_file_path, 'r'))
for line in json_file:
    if line['question']['id'] == "46437095":
        print(line)
