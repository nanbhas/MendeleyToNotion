  
"""
Author: Nandita Bhaskhar
End-to-end script for getting updates from Mendeley on to the Notion Database of your choice
"""

import sys
sys.path.append('../')

import json

from mendeley import Mendeley
from mendeley.session import MendeleySession
from mendeley.auth import MendeleyAuthorizationCodeTokenRefresher, MendeleyAuthorizationCodeAuthenticator

from notion_client import Client

from lib.port_utils import startInteractiveMendeleyAuthorization, getPropertiesForMendeleyDoc
from lib.port_utils import getNotionPageEntryFromPropObj, getAllRowsFromNotionDatabase
from lib.port_utils import portMendeleyDocsToNotion

from lib.utils import *

from globalStore import constants

# arguments
PYTHON = sys.executable
parser = argparse.ArgumentParser()
parser.add_argument('--forceNewLogin', default = False, type = strToBool,
                    help = 'Should it be an interactive session with new login or not')
parser.add_argument('--secretsFilePath', default = None, type = noneOrStr,
                    help = 'secrets file path to be written or overwritten')

# main script
if __name__ == "__main__":

    # parse all arguments
    args = parser.parse_args()

    # read arguments
    forceNewLogin = args.forceNewLogin
    secretsFilePath = args.secretsFilePath

    # open secrets 
    with open(constants.MENDELEY_SECRET_FILE, "r") as f:
        secrets = json.load(f)
    with open(constants.NOTION_SECRET_FILE, "r") as f:
        secrets_notion = json.load(f)

    # initialize mendeley object
    mendeley = Mendeley(client_id = secrets["clientId"], client_secret = secrets["clientSecret"], redirect_uri= secrets["redirectURL"])

    # interactive authorization flow if force new login or if token is absent
    if forceNewLogin or ("token" not in secrets):
        startInteractiveMendeleyAuthorization(mendeley, secretsFilePath)

    assert 'token' in secrets, "Token missing from secrets"

    # start mendeley session
    session = MendeleySession(mendeley, secrets["token"])

    # initialize an authenticator and a refresher
    authenticator = MendeleyAuthorizationCodeAuthenticator(mendeley, session.state())
    refresher = MendeleyAuthorizationCodeTokenRefresher(authenticator)

    # extract refresh token using refresher and activate session
    session = MendeleySession(mendeley, session.token, refresher=refresher)

    # initialize notion client and determine notion DB
    notion = Client(auth = secrets_notion['notionToken'])
    notionDB_id = secrets_notion['databaseID']

    # get list of iterator objects
    obj = []
    for item in session.groups.iter():
        obj.append(item.documents)
    obj.append(session.documents)

    # start porting from mendeley to notion
    noneAU = []
    for ob in obj:
        tmp = portMendeleyDocsToNotion(ob, notion, notionDB_id, noneAU)
        noneAU = noneAU + tmp

    # check the entries with no authors
    try:
        for it in noneAU:
            print(it.title)
    except:
        print('All mendeley entries have non-empty authors')

