from flask import Flask, render_template, request
from threading import Thread
from functools import partial

app=Flask(__name__)

ports={33330: {'pages': {}}, 33331: {'pages': {}}, 33332: {'pages': {}}}

@app.route("/")
def home():
    thisport=int(request.host.split(":")[-1])
    return render_template('home.html', pageids=ports[thisport]['pages'].keys())

@app.route('/post/<pid>')
def page(pid):
    thisport=int(request.host.split(":")[-1])
    try:
        pid=int(pid)
        if pid not in ports[thisport]['pages'].keys():
            return render_template("error.html", error="Page not found.")
    except:
        return render_template("error.html", error="Invalid Page ID.")
    return render_template("page.html", pictures=ports[thisport]['pages'][pid], pageid=pid, allpages=ports[thisport]['pages'].keys())

if __name__=="__main__":

    c=1
    p=1
    images=[]
    for i in range(1, 51):
        if c==11:
            ports[33330]['pages'][p]=images
            images=[]
            p+=1
            c=1
        images.append("{}.jpg".format(i))
        c+=1
    else:
        ports[33330]['pages'][p]=images

    c=1
    p=1
    images=[]
    for i in range(51, 101):
        if c==11:
            ports[33331]['pages'][p]=images
            images=[]
            p+=1
            c=1
        images.append("{}.jpg".format(i))
        c+=1
    else:
        ports[33331]['pages'][p]=images

    c=1
    p=1
    images=[]
    for i in range(101, 151):
        if c==11:
            ports[33332]['pages'][p]=images
            images=[]
            p+=1
            c=1
        images.append("{}.jpg".format(i))
        c+=1
    else:
        ports[33332]['pages'][p]=images

    threads=[]
    for PORT in ports.keys():
        threads.append(Thread(target=partial(app.run, port=PORT, debug=False)))
        threads[-1].start()
