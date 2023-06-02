'''
Note:
When trying to run this project, the regular jwt-library must not be installed.
Instead only the pyJWT library is allowed to be installed.
-> pip uninstall jwt
-> pip install pyJWT
'''

#from github import Github, GithubIntegration
import os
import requests
import jwt
import time
import sys
import base64


pem_file = open("privateKey.pem", "rb")
signing_key = jwt.jwk_from_pem(pem_file.read())

payload = {
    # Issued at time
    'iat': int(time.time()),
    # JWT expiration time (10 minutes maximum)
    'exp': int(time.time()) + 600,
    # GitHub App's identifier
    'iss': os.getenv("GH_APP_ID")
}

# Create JWT
jwt_instance = jwt.JWT()
encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')

#integration = GithubIntegration(os.getenv('GH_APP_ID'), private_key)
#auth = integration.get_access_token(os.getenv('GH_APP_INSTALLATION_ID'))

auth = requests.post("https://api.github.com/app/installations/" + os.getenv("GH_APP_INSTALLATION_ID") + "/access_tokens", headers={
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer " + encoded_jwt
}, json={
    "permissions": {
        "contents": "write"
    },
})

token = auth.json()["token"]

with open("BigData.zip", "rb") as zipfile:
    encoded_string = base64.b64encode(zipfile.read())

# create file
filename = "Archiv_100MB.zip"
req = requests.put("https://api.github.com/repos/" + os.getenv('ORGANIZATION') + "/" + os.getenv("REPO") + "/contents/" + filename, headers={
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer " + token,
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "multipart/form-data"
}, json={
    "message": "test_python",
    "content": encoded_string.decode('utf-8')
})

print(req.json())
print(req.status_code)