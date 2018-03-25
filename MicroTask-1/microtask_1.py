from datetime import datetime
import elasticsearch
import elasticsearch_dsl
from pprint import pprint
import pandas as pd
import numpy as np
from perceval.backends.core.git import Git

# Url for the git repo to analyze
repo_url = 'http://github.com/grimoirelab/perceval.git'

# Directory for letting Perceval clone the git repo
repo_dir = '/tmp/perceval.git'

# ElasticSearch instance (url)
# Assuming your localhost instance is ON , if not initialize it
es = elasticsearch.Elasticsearch('http://localhost:9200/',  verify_certs=False)

enrich_index_name = 'git'

# # Create the 'git' index in ElasticSearch
# try:
#     es.indices.create(enrich_index_name)
# except elasticsearch.exceptions.RequestError:
#     print("deleting")
#     #This will delete the already existing "enrich_index_name" and will create a new one
#     es.indices.delete(enrich_index_name)
#     es.indices.create(enrich_index_name)
#
# repo = Git(uri=repo_url, gitpath=repo_dir)
# for commit in repo.fetch():
#     # Upload the whole body to ElasticSearch .
#     es.index(index='git', doc_type='summary', body=commit)

#alternatively you can also upload by running on terminal :-
#p2o.py --enrich --index git_raw --index-enrich git   -e http://localhost:9200 --no_inc --debug   git https://github.com/grimoirelab/perceval.git

#The above command will do the also upload the index="git" to ElasticSearch


response = es.search(index=enrich_index_name)
Number_of_commits = response['hits']['total']
print("Total Number of commits :- %s" %(Number_of_commits))
response = es.search( index=enrich_index_name , body={"size":Number_of_commits} )

author=[] #declaring a list
output = set() # set funtion in python chooses unique strings

for i in response['hits']['hits']:
    output.add(i['_source']['author_name']) #will add only unique strings to the list

for i in output:
    dictionary = {'Author_Name' : i , 'First_Commit_Date' : 'NA' , 'Total_Number_of_commits' : 0}
    author.append(dictionary)

# for i in author:
#     pprint(i)

for i in response['hits']['hits']:
    # print(author['Author_Name'])
    for j in author:
        if j['Author_Name'] == i['_source']['author_name'] :

            if j['First_Commit_Date'] == "NA":
                #can also do the same the same through this method
                # temp = i['_source']['author_date'].split('T')
                # print(temp[0])
                temp = i['_source']['author_date']
                j['First_Commit_Date'] = datetime.strptime(temp, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m')
            j['Total_Number_of_commits']+=1

s = pd.DataFrame(author)
# s['First_Commit_Date'] = pd.to_datetime(s.First_Commit_Date)
s.sort_values(by = 'First_Commit_Date' , inplace=True)
s.index = range(1,len(s.index)+1)
# pprint(len(s.index))
# pprint(s.First_Commit_Date[len(s.index)])
# last = len(s.index)
temp1 = s.First_Commit_Date[1]
temp2 = s.First_Commit_Date[len(s.index)]
print(temp1,temp2)
# month_commit = pd.date_range( temp1 , temp2, freq='M')
month_commit = pd.date_range(*(pd.to_datetime([temp1, temp2]) + pd.offsets.MonthEnd()), freq='M')

# pprint(month_commit)
month_commit = [i.strftime('%Y-%m') for i in month_commit]
# pprint(month_commit)
commiters_per_month = dict()
# commiters_per_month = []
temp = []
for i in month_commit:
    commiters_per_month[i]=0
# pprint(commiters_per_month)

for i in author:
    commiters_per_month[i['First_Commit_Date']]+=1
#     print(i['First_Commit_Date'])

#
# pprint(commiters_per_month)
# answer = pd.DataFrame.from_dict(commiters_per_month)
answer = pd.DataFrame(list(commiters_per_month.items()), columns=['year-month' , 'Number_of_Commits'])
answer.sort_values(by = 'year-month' , inplace=True)
s.index = range(1,len(s.index)+1)
print(answer)
