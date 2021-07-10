# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# %load_ext autoreload
# %autoreload 2

# %%
import json
import random
import string
import time

# %%
import sys
sys.path.append('../')

# %%
from mendeley import Mendeley

# %%
from mendeley.session import MendeleySession

# %%
from mendeley.auth import MendeleyLoginAuthenticator, MendeleyAuthorizationCodeTokenRefresher
from mendeley.auth import MendeleyAuthorizationCodeAuthenticator

# %%
from notion_client import Client

# %%
from lib.port_utils import startInteractiveMendeleyAuthorization, getPropertiesForMendeleyDoc
from lib.port_utils import getNotionPageEntryFromPropObj, getAllRowsFromNotionDatabase
from lib.port_utils import portMendeleyDocsToNotion

# %%
from datetime import datetime

# %% [markdown]
# ## Config Files

# %%
with open("../secrets/secrets_mendeley.json", "r") as f:
    secrets = json.load(f)

# %%
with open("../secrets/secrets_notion.json", "r") as f:
    secrets_notion = json.load(f)

# %% [markdown]
# ## Start Mendeley Session

# %%
mendeley = Mendeley(client_id = secrets["clientId"], client_secret = secrets["clientSecret"], redirect_uri= secrets["redirectURL"])

# %%
forceNewLogin = False
secretsFilePath = None

# %%
# interactive authorization flow if force new login or if token is absent
if forceNewLogin or ("token" not in secrets):
   startInteractiveMendeleyAuthorization(mendeley, secretsFilePath)

# %%
assert 'token' in secrets, "token missing from secrets"

# %%
session = MendeleySession(mendeley, secrets["token"])

# %%
authenticator = MendeleyAuthorizationCodeAuthenticator(mendeley, session.state())

# %%
refresher = MendeleyAuthorizationCodeTokenRefresher(authenticator)

# %%
session = MendeleySession(mendeley, session.token, refresher=refresher)

# %% [markdown]
# ## Set up import from Mendeley

# %% tags=[] jupyter={"outputs_hidden": true}
for i, item in enumerate(session.documents.iter()):
    print(i, item)

# %%
getNotionPageEntryFromPropObj(getPropertiesForMendeleyDoc(item))

# %% [markdown]
# ## Notion Setup

# %%
notion = Client(auth = secrets_notion['notionToken'])

# %%
notionDB_id = secrets_notion['databaseID']

# %%
for i, item in enumerate(session.groups.iter()):
    print(i, item)

# %%
#for i, item in enumerate(mendeley_session.documents.iter()):
for i, it in enumerate(item.documents.iter()):
    print(i, it.title)
    # check if it's id is in notion
    query = notion.databases.query(
                **{
                    "database_id": notionDB_id,
                    "filter": {"property": "UID", "text": {"equals": it.id}},
                }
            ).get("results")
    
    if len(query) == 1:
        
        print('----1 result matched query')
        
        # last modified time on Mendeley is AFTER last edited time on Notion
        if str(it.last_modified) > query[0]['last_edited_time']:
            print('--------Updating row in notion')
            pageID = query[0]['id']
            propObj = getPropertiesForMendeleyDoc(it)
            notionPage = getNotionPageEntryFromPropObj(propObj)
            notion.pages.update( pageID, properties = notionPage)
            
        else:
            print('--------Nothing to update')
            pass
            
        
    elif len(query) == 0:
        
        print('----No results matched query. Creating new row')
        propObj = getPropertiesForMendeleyDoc(it)
        notionPage = getNotionPageEntryFromPropObj(propObj)
        notion.pages.create(parent={"database_id": notionDB_id}, properties = notionPage)
        
    else:
        raise NotImplementedError

# %%
hasMore = True
allNotionRows = []
i = 0

# %%
while hasMore:
    if i == 0:
        query = notion.databases.query(
                        **{
                            "database_id": notionDB_id,
                            #"filter": {"property": "UID", "text": {"equals": it.id}},
                        }
                    )
    else:
        query = notion.databases.query(
                        **{
                            "database_id": notionDB_id,
                            "start_cursor": nextCursor,
                            #"filter": {"property": "UID", "text": {"equals": it.id}},
                        }
                    )
        
    allNotionRows = allNotionRows + query['results']
    nextCursor = query['next_cursor']
    hasMore = query['has_more']
    i+=1

# %%
len(allNotionRows)

# %%
xx = getAllRowsFromNotionDatabase(notion, notionDB_id)

# %%
notionRow = [row for row in xx if row['properties']['UID']['rich_text'][0]['text']['content'] == '3']


# %%
# !pip install tqdm

# %%
dbID = "6314e22663b04477959bb0de89806260"
obj = []
for item in session.groups.iter():
    obj.append(item.documents)
obj.append(session.documents)

# %% tags=[]
noneAU = []
for ob in obj:
    tmp = portMendeleyDocsToNotion(ob, notion, notionDB_id, noneAU)
    noneAU = noneAU + tmp

# %%
it = next(obj[0].iter())

# %%
it.last_modified

# %%
allNotionRows = getAllRowsFromNotionDatabase(notion, notionDB_id)

# %%
notionRow = [row for row in allNotionRows if row['properties']['UID']['rich_text'][0]['text']['content'] == it.id]

# %%
notionRow = notionRow[0]

# %%
notionRow['last_edited_time']

# %%
import arrow

# %%
t = notionRow['last_edited_time']

# %%
mt = it.last_modified

# %%
mt.to('US/Pacific')

# %%
t

# %%
mt

# %%
arrow.get(t)

# %%
mt.format('YYYY-MM-DD HH:mm:ss ZZ')

# %%
arrow.get(t).format('YYYY-MM-DD HH:mm:ss ZZ')

# %%
mt.to('US/Pacific') < arrow.get(t).to('US/Pacific')

# %%

# %%

# %%

# %%
noneAuthors = []
for i, it in enumerate(mendeley_session.documents.iter()):
#for i, it in enumerate(item.documents.iter()):

    print(i, it.title)
    
    if it.authors is not None:
        # check if its id is in notion
        
        notionRow = [row for row in allNotionRows if row['properties']['UID']['rich_text'][0]['text']['content'] == it.id]
         
        numMatches = len(notionRow)
        if numMatches == 1:
            notionRow = notionRow[0] 
        
        assert numMatches < 2, "Duplicates are present in the notion database"
        

        if numMatches == 1:

            print('----1 result matched query')

            # last modified time on Mendeley is AFTER last edited time on Notion
            if str(it.last_modified) > notionRow['last_edited_time']:
                print('--------Updating row in notion')
                pageID = notionRow['id']
                propObj = getPropertiesForMendeleyDoc(it)
                notionPage = getNotionPageEntryFromPropObj(propObj)
                notion.pages.update( pageID, properties = notionPage)

            else:
                print('--------Nothing to update')
                pass


        elif numMatches == 0:

            print('----No results matched query. Creating new row')
            propObj = getPropertiesForMendeleyDoc(it)
            notionPage = getNotionPageEntryFromPropObj(propObj)
            notion.pages.create(parent={"database_id": notionDB_id}, properties = notionPage)

        else:
            raise NotImplementedError
    else:
        noneAuthors.append(it)

# %%
notionRow

# %%
print(i, it.title)

# %%
it.id

# %%
# check if it's id is in notion
query = notion.databases.query(
            **{
                "database_id": notionDB_id,
                "filter": {"property": "UID", "text": {"equals": it.id}},
            }
        ).get("results")
query

# %%
if len(query) == 1:

    print('----1 result matched query')

    # last modified time on Mendeley is AFTER last edited time on Notion
    if str(it.last_modified) > query[0]['last_edited_time']:
        print('--------Updating row in notion')
        pageID = query[0]['id']
        propObj = getPropertiesForMendeleyDoc(it)
        notionPage = getNotionPageEntryFromPropObj(propObj)
        notion.pages.update( pageID, properties = notionPage)

    else:
        print('--------Nothing to update')
        pass


elif len(query) == 0:

    print('----No results matched query. Creating new row')
    propObj = getPropertiesForMendeleyDoc(it)
    notionPage = getNotionPageEntryFromPropObj(propObj)
    notion.pages.create(parent={"database_id": notionDB_id}, properties = notionPage)

else:
    raise NotImplementedError

# %%
