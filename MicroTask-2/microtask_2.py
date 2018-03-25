from datetime import datetime
import elasticsearch
import elasticsearch_dsl
from pprint import pprint
from perceval.backends.core.github import GitHub
import pandas as pd
import subprocess
import matplotlib.pyplot as plt


enrich_index_name = 'github'
raw_index_name = 'github_raw'

es = elasticsearch.Elasticsearch('http://localhost:9200/',  verify_certs=False)

github_token = "6ee78bdbfde11ffd95c0c1b22ed5bc1a6f1fd52a"

# if(es.indices.exists(enrich_index_name)):
#     es.indices.delete(enrich_index_name)
#
# if(es.indices.exists(raw_index_name)):
#     es.indices.delete(raw_index_name)

# subprocess.run(['p2o.py', '--enrich', '--index', raw_index_name,
#       '--index-enrich', enrich_index_name, '-e', 'http://localhost:9200/',
#       '--no_inc', '--debug', 'github', 'grimoirelab' , 'perceval',
#       '-t', github_token, '--sleep-for-rate'])

response = es.search(index=enrich_index_name)
Number_of_commits = response['hits']['total']
print("Total Number of commits :- %s" %(Number_of_commits))
response = es.search( index=enrich_index_name , body={"size":Number_of_commits} )

# for i in response['hits']['hits']:
#     pprint(i['_source'])


request = elasticsearch_dsl.Search(using=es, index=enrich_index_name)
request = request.source(['created_at', 'closed_at', 'time_open_days' , 'time_to_close_days' , 'item_type' , 'id_in_repo'])
request = request.filter("terms", item_type = ['issue'])
request = request.filter('range', created_at ={'gte': 'now-6M'})
request = request.sort({'created_at':{'order':'asc'}})
request = request[0:10000]
result = request.execute()


# pprint(request.to_dict())
# pprint(result.to_dict())

result = result.to_dict()
data = []

for i in result['hits']['hits']:
    data.append(i['_source'])

# pprint(data)

df = pd.DataFrame(data)
df = df.fillna(0)
# pprint(df['id_in_repo'])

ax = df.plot(x=df['id_in_repo'], kind='bar', figsize=(20, 15))
ax.set_title('Issues for the last 6 months')
ax.set_xlabel('Issue number')
ax.set_ylabel('Days open')
plt.savefig('graph.png', bbox_inches='tight')
plt.show()
