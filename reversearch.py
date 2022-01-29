import base64
import requests

def getCloudAPIDetails(imagepath):
    url = "https://api.bing.microsoft.com/v7.0/images/visualsearch"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'
        }
    with open(imagepath, 'rb') as f:
        imageuri=base64.b64encode(f.read()).decode()
    r=requests.post(url+"?image="+imageuri, headers=headers)
    print(r.content)

getCloudAPIDetails("12.jpg")