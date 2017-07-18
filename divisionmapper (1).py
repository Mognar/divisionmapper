
# coding: utf-8

# In[17]:

get_ipython().system(u'pip install requests-cache')
get_ipython().system(u'pip install pyGithub')
from github import Github
g = Github([github ID goes here])


# In[18]:

import json
import requests
import requests_cache
import urllib.parse


# In[19]:

requests_cache.install_cache('divisions_cache', backend='sqlite')


# In[20]:

stub='http://lda.data.parliament.uk'.strip('/')


# In[21]:

def getURL(url):
    print(url)
    r=requests.get(url)
    print(r.status_code)
    return r

#Should build a proper recursive loader
def loader(url):
    items=[]
    done=False
    r=getURL(url)
    while not done:
        items=items+r.json()['result']['items']
        if 'next' in r.json()['result']:
            r=getURL(r.json()['result']['next']+'&_pageSize=20')
        else: 
            done=True
    return items


# In[22]:

url='{}/{}.json?session={}&{}'.format(stub,'commonsdivisions','2017/19','_view=all')
items=loader(url)


# In[23]:

items[0]


# In[24]:

rem =[]
rel =[]
rep =[]
#rez = (rel,rep)
for i in items:
    votes = i['vote']
    for m in votes: 
        if "//" in m:
            param, value = m.split("//",1)
            n = 'http://lda.{}.json'.format(value)
            nn = requests.get(n)
            #for z in nn:
            nnm =(nn.json()['result']['primaryTopic']['memberPrinted']['_value'])
            nnn =(nn.json()['result']['primaryTopic']['member'][0]['_about'])
            nnp =(nn.json()['result']['primaryTopic']['memberParty'])
            if "//" in nnn:
                param, value = nnn.split("//",1)
                x = 'http://lda.{}.json'.format(value)
                xx = requests.get(x)
                xxx =(xx.json()['result']['primaryTopic']['constituency']['_about'])
                if "//" in xxx:
                    param, value = xxx.split("//",1)
                    c= 'http://lda.{}.json'.format(value)
                    cc = requests.get(c)
                    ccc = (cc.json()['result']['primaryTopic']['gssCode'])
                    #print(ccc)
            rem.append(nnm)        
            rel.append(ccc)
            rep.append(nnp)
#print(rel)            
            
    


# In[25]:

import pandas as pd
pd.set_option('display.max_columns', 5400)


# In[26]:

#df=pd.DataFrame(rel,rep)
data_frame = pd.DataFrame(rel)
data_frame[1] = pd.Series(rem)
data_frame[2] = pd.Series(rep)
#dm=pd.DataFrame(rep)
#dfg=pd.concat([df, dm], axis=1)
dfc=data_frame.groupby([rel,rem,rep]).count().reset_index()
dfc.columns=['Constituency','MP','Party','Divs','2','3']#,'No. of divisions','yes']
dfs=dfc.sort_values(by='MP', ascending=0)
dffinal = dfs[['Constituency','MP','Party','Divs']]#,'No. of divisions']]
#dfr=dfs.head(n=100)
#dffinal=dfz.to_string


# In[27]:

print(dffinal)


# In[28]:

indexed_df = dffinal.set_index(['Constituency'])
idf=indexed_df.to_json(orient='index')
idf1 = idf.replace("'", "")
idff = json.loads(idf1)
jsonobj = {"layout":"odd-r","hexes":{}}  

jsonobj["hexes"] = (idff)
#jsonout = jsonobj.replace("'", "")
json1 = json.dumps(jsonobj)
print(json1)


# In[29]:

get_ipython().system(u'pip install jsonmerge')
from jsonmerge import merge


# In[30]:

head = jsonobj
with open('/resources/data/test.hexjson') as json_data:
    base = json.load(json_data)
    #print(base)
schema = {
            "properties": {
                "bar": {
                    "mergeStrategy": "append"
                 }
             }
         }

from jsonmerge import Merger
merger = Merger(schema)
result = merger.merge(base, head)
jsonfinal = json.dumps(result)
print(jsonfinal)


# In[31]:

from datetime import datetime
timenow= str(datetime.now())
user = g.get_user()
repo = user.get_repo("divisionmap")
print(repo)
file = repo.get_file_contents("/tst.hexjson")
print(file)
repo.update_file("/tst.hexjson", timenow, jsonfinal, file.sha)

