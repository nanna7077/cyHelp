import shutil
import os
import requests
import lxml
from bs4 import BeautifulSoup
import smokesignal

knownUrls=[]
urlsToSearch=set()
externalurls=set()
searched=set()

imageurls=set()
images=list()

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'
}

def crawlForUrls(baseurl, url):
    url=url.strip('/')
    if baseurl+url in searched:
        return
    try:
        req=requests.get(baseurl+url, headers=headers)
    except Exception as err:
        smokesignal.emit("error", "Could not create request", str(err))
        return
    if req:
        soup=BeautifulSoup(req.content, 'lxml')
        for l in soup.find_all('a'):
            if l['href'][0]=='/':
                if url+l['href'] not in searched:
                    searched.add(baseurl+url)
                    urlsToSearch.add(baseurl+l['href'].strip('/'))
                    crawlForUrls(baseurl, l['href'])
            else:
                externalurls.add(l['href'])
    else:
        smokesignal.emit("error", "Could not reach URL", req.content)

def getImages(baseurl, url):
    baseurl=baseurl.strip("/")
    req=requests.get(url, headers=headers)
    if req:
        soup=BeautifulSoup(req.content, 'lxml')
        for img in soup.find_all('img'):
            imageurls.add(baseurl+img['src'])
    else:
        smokesignal.emit("error", "Could not reach URL for Image", req.content)

@smokesignal.on("knownurlschanged")
def knownurlsChanged():
    with open('knownurls.txt', 'r') as file:
        for line in file:
            knownUrls.append(line.strip())
    smokesignal.emit("refreshimagescache")

@smokesignal.on("refreshimagescache")
def refreshImagesCache():
    for url in knownUrls:
        crawlForUrls(url, "/")

    for l in urlsToSearch:
        getImages(url, l)
    
    shutil.rmtree('cache')
    os.mkdir('cache')
    
    c=0
    for i in imageurls:
        req=requests.get(i, headers=headers)
        if req:
            with open("cache/{}.{}".format(c, req.headers.get('content-type').split("/")[-1]), 'wb') as imagefile:
                imagefile.write(req.content)
            images.append({'image': "cache/{}.{}".format(c, req.headers.get('content-type').split("/")[-1]), 'link': i})
        else:
            smokesignal.emit('error', 'Could not download Image for cache', req.content)
        c+=1

    smokesignal.emit("imagescacherefreshed")
    #smokesignal.emit('startcomparison', ['12.jpg'])

#smokesignal.emit('knownurlschanged')