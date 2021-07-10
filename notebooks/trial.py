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
import pickle as pkl

# %%
from mendeley import Mendeley

# %%
from mendeley.session import MendeleySession

# %%
from mendeley.auth import MendeleyLoginAuthenticator, MendeleyAuthorizationCodeTokenRefresher
from mendeley.auth import MendeleyAuthorizationCodeAuthenticator

# %%
from oauthlib.oauth2 import MobileApplicationClient, BackendApplicationClient, WebApplicationClient

# %%
from notion_client import Client

# %% [markdown]
# ## Config Files

# %%
with open("secrets_mendeley.json", "r") as f:
    secrets = json.load(f)

# %%
with open("secrets_notion.json", "r") as f:
    secrets_notion = json.load(f)

# %% [markdown]
# # Trial using alt sources

# %%
with open("secrets_mendeley_token.json", "r") as f:
    secrets = json.load(f)

# %%
mendeley = Mendeley(client_id = secrets["clientId"], client_secret = secrets["clientSecret"], redirect_uri= secrets["redirectURL"])

# %%
session = MendeleySession(mendeley, secrets["token"])

# %%
authenticator = MendeleyAuthorizationCodeAuthenticator(mendeley, session.state())

# %%
refresher = MendeleyAuthorizationCodeTokenRefresher(authenticator)

# %%
sessionTrial = MendeleySession(mendeley, session.token, refresher=refresher)

# %%
for i, item in enumerate(sessionTrial.documents.iter()):
    print(i, item)

# %%
time.time()

# %%
from datetime import datetime

# %%
datetime.fromtimestamp(1625883885.0438263)

# %%
datetime.fromtimestamp(time.time())

# %%

# %%
session = MendeleySession(mendeley, secrets["token"])

# %%
for i, item in enumerate(session.documents.iter()):
    print(i)

# %%

# %%

# %%
auth = mendeley.start_authorization_code_flow()

# %%
state = auth.state

# %%
state

# %%
auth = mendeley.start_authorization_code_flow( state = state )

# %%
print(auth.get_login_url())

# %%
redirect = "https://stanford.edu/~nanbhas/?code=9wuJl29pvPtUq0HHvJdLzR2FGZ4&state=7A0TYULKQFKRUEM88K8YGIOA86WP68"

# %%
session = auth.authenticate(redirect)

# %%
session.token

# %%
secrets['token'] = session.token

# %%

# %%
with open("secrets_mendeley_token.json", "w") as f:
    json.dump(secrets, f)

# %%

# %%

# %%

# %%

# %% [markdown]
# ## Set up import from Mendeley

# %%
mendeley = Mendeley(client_id = secrets["clientId"], client_secret = secrets["clientSecret"], redirect_uri= "https://stanford.edu/~nanbhas")

# %%
auth = mendeley.start_authorization_code_flow()

# %%
# The user needs to visit this URL, and log in to Mendeley.
login_url = auth.get_login_url()

# %%
print(login_url)

# %%
request_url = "https://stanford.edu/~nanbhas/?code=zs0bJRtgXZ5nWIjv8ADZlausMII&state=BXOZ678XOE3TZ3QGOIP6EQ3X1VHQE3"

# %%
#state = "D8RZL4TAUZD0PEKXOZF7ZLPMOIFKDV"
#code = "FYw89IMFnW9loP1Pl4rhWl2I-uE"

# %%
#auth = mendeley.start_authorization_code_flow(state)
mendeley_session = auth.authenticate(request_url)

# %%
with open('session.pkl', 'wb') as f:
    pkl.dump(mendeley_session, f)

# %%
with open('session.pkl', 'rb') as f:
    mendeley_session1 = pkl.load(f)

# %%
mendeley_session1.request

# %%
mendeley_session = MendeleySession()


# %% [markdown]
# ## Functions

# %%
def getPropertiesForMendeleyDoc(docObj, 
            localPrefix = 'file:///C:/Users/Nandita%20Bhaskhar/Documents/5_Others/1_GoogleDrive/Literature%20Review/'):
    
    prop = {}

    prop['Citation'] = str(docObj.authors[0].last_name) + str(docObj.year)
    prop['Title'] = str(docObj.title)
    prop['UID'] = str(docObj.id)
    
    try:
        for key, value in docObj.identifiers.items():
            if key in ['doi', 'arxiv', 'pmid', 'issn', 'isbn']:
                prop[key.upper()] = value
    except:
        pass
    
    prop['Created At'] = str(docObj.created)
    prop['Last Modified At'] = str(docObj.last_modified)
    prop['Abstract'] = str(docObj.abstract)[:2000]
    prop['Authors'] = ', '.join([str(author.first_name) + ' ' + str(author.last_name) for author in docObj.authors])
    prop['Year'] = str(docObj.year)
    prop['Type'] = str(docObj.type)
    prop['Venue'] = str(docObj.source)
    
    if len(docObj.authors) > 3:
        fileName = str(docObj.authors[0].last_name) + ' et al.' + '_' + prop['Year'] + '_' + prop['Title'].replace(':','') + '.pdf'
        prop['Filename'] = fileName
        prop['Filepath'] = localPrefix + fileName
        
    else:
        fileName = ', '.join([str(author.last_name) for author in docObj.authors])
        fileName = fileName + '_' + prop['Year'] + '_' + prop['Title'].replace(':','') + '.pdf'
        prop['Filename'] = fileName
        prop['Filepath'] = localPrefix + fileName
        
    bibtex = '@article{' + prop['Citation'] + ', \n' + \
            'author = {' + ' and '.join([str(author.last_name) + ', ' + str(author.first_name) for author in docObj.authors]) + '}, \n' + \
            'journal = {' + prop['Venue'] + '}, \n' + \
            'title = {' + prop['Title'] + '}, \n' + \
            'year = {' +  prop['Year'] + '} \n' + '}'
            
    prop['BibTex'] = bibtex
        
    return prop
    


# %%
def getNotionPageEntryFromPropObj(propObj):
    
    dateKeys = {'Created At', 'Last Modified At'}
    urlKeys = {'Filepath'}
    titleKeys = {'Citation'}
    textKeys = set(propObj.keys()) - dateKeys - titleKeys - urlKeys
    newPage = {
        "Citation": {"title": [{"text": {"content": propObj['Citation']}}]}
    }
    
    for key in textKeys:
        newPage[key] = {"rich_text": [{"text": { "content": propObj[key]}}]}    
    
    for key in dateKeys:
        newPage[key] = {"date": {"start": propObj[key] }}
        
    for key in urlKeys:
        newPage[key] = {"url": propObj[key]}
    
    return newPage


# %% [markdown]
# # Trial

# %%
notion = Client(auth=secrets_notion['notionToken'])

# %%
# Research Lit Review: 690abe1df3664a4eb53485b18185178e
# Mendeley Trial: 6314e22663b04477959bb0de89806260
notionDB_id = "690abe1df3664a4eb53485b18185178e"
#notionDB_id = "6314e22663b04477959bb0de89806260"

# %%
for i, item in enumerate(mendeley_session1.groups.iter()):
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
        
        assert numMatches < 2
        

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
notionRow[0]

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
