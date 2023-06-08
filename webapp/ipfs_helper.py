import requests
import json
from io import BytesIO

IPFS_API_URL = "http://127.0.0.1:5001/api"

def ipfs_upload(fileName, file):

    url = IPFS_API_URL + "/v0/add"
    
    payload = {}
    
    files=[
        ("path",(fileName,file,"text/plain"))
    ]
    
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files) 

    response_dict = json.loads(response.text) # Name, Hash, Size

    return response_dict 


def ipfs_download(cid):

    url = f"http://127.0.0.1:8080/ipfs/{cid}"

    response = requests.request("GET", url) 

    file_bytes = BytesIO(response.content)

    return file_bytes