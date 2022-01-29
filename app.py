from datetime import datetime
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
import os
import smokesignal
import storage
import imagecompare
import reversearch

app=Flask(__name__)
app.secret_key=os.urandom(12)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    email=request.form.get('email')
    if ((email==None) or email.replace(" ", '')==0 or storage.emailExists(email)):
        return render_template("signup.html", error="Invalid Email Address.")
    username=request.form.get('username')
    if ((username==None) or username.replace(" ", '')==0 or storage.usernameExists(email)):
        return render_template("signup.html", error="Invalid username.")
    password=request.form.get('password')
    confirmpassword=request.form.get('password')
    if password!=confirmpassword:
        return render_template("signup.html", error="Password's don't match.")
    if len(password)<5:
        return render_template("signup.html", error="Password does not meet requirements.")
    if storage.createUser(username, email, password):
        return redirect('/login')
    else:
        return render_template("signup.html", error="Internal error in creating user.")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('userid')!=None:
        return redirect('/home')
    if request.method=="GET":
        return render_template('login.html')
    username=request.form.get('username')
    password=request.form.get('password')
    userid, status=storage.checkCredentials(username, password)
    if status:
        session['userid']=userid
        session['username']=username
        return redirect('/home')
    else:
        return render_template('login.html', error="Incorrect username or password.")

@app.route('/home')
def userhome():
    if session.get('userid')==None:
        return redirect('/login')
    currentsearches=[]
    for i in storage.getCurrentSearches(session.get('userid')):
        print(i[1])
        newi=list(i)
        newi[1]=datetime.fromtimestamp(int(float(newi[1]))).strftime("%Y-%m-%d %H:%M:%S")
        currentsearches.append(newi)
    return render_template('userhome.html', currentsearches=currentsearches, username=session.get('username'))

@app.route("/search/new/imageunknown", methods=['POST'])
def createSearchImageUnknown():
    if session.get('userid')==None:
        return redirect('/login')
    uploaded_files=list(request.files.getlist('images'))
    if uploaded_files==[]:
        return render_template('userhome.html', currentsearches=storage.getCurrentSearches(session.get('userid')), username=session.get('username'), error="Please upload a valid image.")
    filenames=""
    for file in uploaded_files:
        file.save(os.path.join('static/upload', secure_filename(file.filename).replace(";", '')))
        filenames+=secure_filename(file.filename).replace(";", '')+";"
    filenames=filenames.strip(";")
    sid, status=storage.createSearch(session.get('userid'), filenames, "NOTCOMPLETE", "NOTCOMPLETE", True)
    if status:
        # return redirect('/search/view/{}'.format(sid))
        return redirect('/home')
    return redirect('/home')

@app.route('/search/new/imageknown', methods=['POST'])
def createSearchImageKnown():
    if session.get('userid')==None:
        return redirect('/login')
    uploaded_files=list(request.files.getlist('images'))
    if uploaded_files==[]:
        return render_template('userhome.html', currentsearches=storage.getCurrentSearches(session.get('userid')), username=session.get('username'), error="Please upload a valid image.")
    filenames=""
    for file in uploaded_files:
        file.save(os.path.join('static/upload', secure_filename(file.filename).replace(";", '')))
        filenames+=secure_filename(file.filename).replace(";", '')+";"
    filenames=filenames.strip(";")
    sid, status=storage.createSearch(session.get('userid'), filenames, "NOTREQUIRED", "NOTCOMPLETE", True)
    if status:
        # return redirect('/search/view/{}'.format(sid))
        return redirect('/home')
    return redirect('/home')

@app.route("/helpRegisterComplaint/<searchid>")
def helpRegisterComplaint(searchid):
    if not storage.checkSearchId(searchid):
        return render_template("error.html", error="Invalid Search ID.")
    return render_template("createcomplaint.html", search=storage.getSearch(searchid))

storage.init()
smokesignal.emit('knownurlschanged')

if __name__=='__main__':
    PORT=os.environ.get('PORT')
    if PORT==None:
        PORT=8080
    app.run(port=PORT, debug=True)
