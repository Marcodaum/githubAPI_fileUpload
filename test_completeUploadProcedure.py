import requests
import base64
import os
import jwt
import time
import sys


appId = os.getenv("GH_APP_ID")
installationId = os.getenv("GH_APP_INSTALLATION_ID")
owner = os.getenv('ORGANIZATION')
repo = os.getenv("REPO")


pem_file = open("privateKey.pem", "rb")
signing_key = jwt.jwk_from_pem(pem_file.read())

payload = {
    # Issued at time
    'iat': int(time.time()),
    # JWT expiration time (10 minutes maximum)
    'exp': int(time.time()) + 600,
    # GitHub App's identifier
    'iss': appId
}

# Create JWT
jwt_instance = jwt.JWT()
encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')


# Set the API endpoint and parameters
url = 'https://api.github.com/repos/' + owner + '/' + repo + '/git'

# Set the path of the file you want to commit
filepath = 'BigData_50er.zip'

# Set the commit message and branch name
commit_message = '50MB_test'
branch_name = 'main'

# Set your GitHub access token for authentication
auth = requests.post("https://api.github.com/app/installations/" + installationId + "/access_tokens", headers={
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer " + encoded_jwt
}, json={
    "permissions": {
        "contents": "write"
    },
})

access_token = auth.json()["token"]


# Open the file in binary mode and read its contents
with open(filepath, 'rb') as f:
    filedata = f.read()

# Encode the file contents as base64
encoded_data = base64.b64encode(filedata).decode()


# Get sha of last commit
shaOfLastCommitUrl = 'https://api.github.com/repos/' + owner + '/' + repo + '/branches/' + branch_name
response = requests.get(shaOfLastCommitUrl, auth=('token', access_token))
shaOfLastCommit = response.json()['commit']['sha']


# Create a new blob by posting the file contents to the API
blob_url = url + '/blobs'
blob_payload = {
    'content': encoded_data,
    'encoding': 'base64'
}
response = requests.post(blob_url, auth=('token', access_token), json=blob_payload)
if response.status_code >= 300:
    print(response.json()['message'] + '. Please try again later.')
    sys.exit()
blob_sha = response.json()['sha']

# Create a new tree object with the new blob
tree_url = url + '/trees'
tree_payload = {
    'base_tree': branch_name,
    'tree': [
        {
            'path': filepath,
            'mode': '100644',
            'type': 'blob',
            'sha': blob_sha
        }
    ]
}
response = requests.post(tree_url, auth=('token', access_token), json=tree_payload)
tree_sha = response.json()['sha']

# Create a new commit with the new tree object
commit_url = url + '/commits'
commit_payload = {
    'message': commit_message,
    'tree': tree_sha,
    'parents': [shaOfLastCommit]
}
response = requests.post(commit_url, auth=('token', access_token), json=commit_payload)
commit_sha = response.json()['sha']

# Update the branch to point to the new commit
ref_url = url + '/refs/heads/' + branch_name
ref_payload = {
    'sha': commit_sha
}
response = requests.patch(ref_url, auth=('token', access_token), json=ref_payload)

# Check if the request was successful
if response.status_code == 200:
    # Print the response JSON
    print(response.json())
else:
    # Print the error message
    print('Error:', response.status_code, response.text)