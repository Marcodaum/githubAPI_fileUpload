'''
Note:
When trying to run this project, the regular jwt-library must not be installed.
Instead only the pyJWT library is allowed to be installed.
-> pip uninstall jwt
-> pip install pyJWT
'''

from github import Github, GithubIntegration
from github.AppAuthentication import AppAuthentication
import os

class Github:

    private_key = open("privateKey.pem", "r").read()
    
    integration = GithubIntegration(os.getenv('GH_APP_ID'), private_key)
    auth = integration.get_access_token(os.getenv('GH_APP_INSTALLATION_ID'))
    access_token = auth.token
    print(access_token)