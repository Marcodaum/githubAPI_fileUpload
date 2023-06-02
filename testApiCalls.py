'''
Note:
When trying to run this project, the regular jwt-library must be installed.
Furthermore the pyJWT library shall be installed.
-> pip install jwt
-> pip install pyJWT
'''

import jwt
import time
import sys
import requests
import base64
import os

github_base_url = "https://api.github.com/"
pem = "privateKey.pem"

# Open PEM
with open(pem, 'rb') as pem_file:
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

print(f"JWT:  {encoded_jwt}")


# Get information
test_req = requests.get(github_base_url + "app/installations", headers={
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer " + encoded_jwt,
    "X-GitHub-Api-Version": "2022-11-28"
})

print(test_req.json())


# List repos
repo_req = requests.get(github_base_url + "orgs/" + os.getenv("ORGANIZATION") + "/repos", headers={
    "Accept": "application/vnd.github+json",
    "Authorization": encoded_jwt,
    "X-GitHub-Api-Version": "2022-11-28"
})

print(repo_req.json())


# Create a blob
blob_req = requests.post(github_base_url + "repos/" + os.getenv("ORGANIZATION") + "/" + os.getenv("REPO") +  "/git/blobs", headers={
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer " + encoded_jwt,
    "X-GitHub-Api-Version": "2022-11-28"
}, json={
  "owner": os.getenv("ORGANIZATION"),
  "repo": os.getenv("REPO"),
  "content": "test",
  "encoding": 'utf-8',
  "Content-Type": "multipart/form-data"
})

print(blob_req.json())


# List installations
installations_req = requests.get(github_base_url + "app/installations", headers={
    "Accept": "application/vnd.github+json",
    "Authorization": "token " + os.getenv('PERSONAL_PRIVATE_KEY'),
    "X-GitHub-Api-Version": "2022-11-28"
})

print(installations_req.json())