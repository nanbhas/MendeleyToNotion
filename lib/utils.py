  
"""
Author: Nandita Bhaskhar
Misc. helper functions
"""

import os
import sys
sys.path.append('../')

import json

from mendeley import Mendeley
from mendeley.session import MendeleySession


def startInteractiveMendeleyAuthorization(mendeley, secretsFilePath = None):
    '''
    Start an interactive OAuth flow
    Args:
        mendeley: (Mendeley) a Mendeley Class object
        secretsFilePath: (str) optional - path of the json file to store secrets
    Returns:
        No return value
        Generates session token after user authorization and then
            either prints it or writes to a json file
    '''
    auth = mendeley.start_authorization_code_flow()
    state = auth.state
    auth = mendeley.start_authorization_code_flow( state = state )
    print(auth.get_login_url())

    # After logging in, the user will be redirected to a URL, auth_response.
    session = auth.authenticate( input() )

    if secretsFilePath:
        assert secretsFilePath.endswith('.json'), "secretsFilePath should be a json file"

        if os.path.isfile(secretsFilePath):
            with open(secretsFilePath, "r") as f:
                secrets = json.load(f)
        else: 
            secrets = {}

        secrets['token'] = session.token

        with open(secretsFilePath, "w") as f:
            json.dump(secrets, f)
    else:
        print(session.token)


def getPropertiesForMendeleyDoc(docObj, localPrefix = 'file:///C:/Users/Nandita%20Bhaskhar/Documents/5_Others/1_GoogleDrive/Literature%20Review/'):
    '''
    Gets all properties of a document object in Mendeley as a dict
    Args:
        docObj: (mendeley.models.documents.UserDocument object) 
        localPrefix: (Str) local filepath prefix to be added to the filename
    Returns:
        prop: (dict) containing all relevant document keys
                Citation, Title, UID, ..., 
    '''
    
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


def getNotionPageEntryFromPropObj(propObj):
    '''
    Format the propObj dict to Notion page format
    Args:
        propObj: (dict)
    Returns:
        newPage: (Notion formated dict)
    '''
    
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
    

