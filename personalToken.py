import jwt
import time
import sys
import requests
import base64
import json
import os

with open("testproject.zip", "rb") as zipfile:
    encoded_string = base64.b64encode(zipfile.read())

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
    'iss': os.getenv('GH_APP_ID')
}

# Create JWT
jwt_instance = jwt.JWT()
encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')

# set scopes
req = requests.post("https://api.github.com/app/installations/" + os.getenv('GH_APP_INSTALLATION_ID') + "/access_tokens", headers={
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer " + encoded_jwt,
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "multipart/form-data"
    },
    json={  
        "repository": os.getenv('REPO'),
        "permissions": {
            "issues": 'write',
            "contents": 'write'
    }
})

print(req.json())


# create file
filename = "test_project.zip"
req = requests.put("https://api.github.com/repos/" + os.getenv('ORGANIZATION') + "/" + os.getenv("REPO") + "/contents/" + filename, headers={
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer " + encoded_jwt,
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "multipart/form-data"
}, json={
    "message": "test_python",
    "content": encoded_string.decode('utf-8')
})

print(req.json())