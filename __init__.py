from flask import Flask,render_template,redirect,request,url_for,flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from setupDB import Post, Base, User
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2 
import json
import requests
from flask import make_response 



CLIENT_ID = json.loads(open('client_secrets.json','r').read()) ['web'] ['client_id']


#Configuration
engine = create_engine('sqlite:///PostsUser.db',
connect_args={'check_same_thread': False})
Base.metadata.create_all(engine) 
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

def getApp():
    return app

def createUser(login_session):
    newUser = User( name = login_session['name'],
                    email = login_session['email'],
                    picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

def getUser(user_id):
    result = session.query(User).get(user_id)
    return result    

def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None 

@app.route('/')
def indexRoute():
    all_posts = session.query(Post).all()
    if 'email' not in login_session:
        logged_in = False
        your_posts = []
    else:
        id = getUserId(login_session['email'])
        your_posts = session.query(Post).filter_by(user_id = id).all()
        logged_in = True
    
    return render_template('index.html',all_posts = all_posts, your_posts = your_posts
    ,all_size = len(all_posts),your_size = len(your_posts),logged_in = logged_in)

@app.route('/login')
def login():
    #generating anti-forgery state token
    state = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))    
    login_session['state'] = state
    return render_template('login.html',STATE = state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print('Inavlid state token')
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object which contains
        # access token
        #creating oauth flow object by passing credentials 
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        # specify with postmessage that the server is sending off the one time 
        # authorization code
        oauth_flow.redirect_uri = 'postmessage'
        # finally exchange the one time authorization code for credentials object
        credentials = oauth_flow.step2_exchange(code)
    #if there was an error, an a FlowExchangeError exception will be thrown    
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print('FlowExchangeError')
        return response

    # Get access token from the credentials object
    access_token = credentials.access_token
    # google api validates the acces token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # get request to store the result       
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error dueing GET, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        print('GET Error')
        return response

    # Verify that the result object with validated access token 
    # has the same user id as the user id
    # in the credentials object
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        print('Valid acces token but not same user')
        return response

    # Verify that the result object with 
    # validated access token has same client id as original client id.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        print('mismatch in client id')
        return response

    # Check if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        print('user is already logged in')
        return response

    # if none of the if statements are triggered, we have a valid access token
    # and user is signed in. They can now make API calls and we have the info
    print('No coditions triggered')    

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    # data is json with all the user's info
    data = answer.json()

    #storing info in login session
    login_session['gplus_id'] = gplus_id
    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    #storing user info in database
    user_id = getUserId(login_session['email'])
    if not user_id:
        createUser(login_session)
    login_session['user_id'] = user_id


    #display redirect message
    output = ''
    output += '<h1>Welcome, '
    output += login_session['name']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['name'])
    return output

@app.route('/gdisconnect')
def gdisconnect():
    #get the current session's acces token
    access_token = login_session.get('access_token')

    #user is no logged in so no need to log out
    if access_token is None:
        print ('No user logged in')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['name'])
    # revoke the token to log out
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    # result stores the returned json object
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)

    # if successful delete all info from the login session
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['name']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        del login_session['user_id']
    

        response = make_response(json.dumps('Successfully disconnected. Thank You for Visiting!! '), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # if there was some error    
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/fbconnect',methods=['POST'])
def fbconnect():
    #check state
    if login_session['state'] != request.args.get('state'):
        response = make_response(json.dumps('Wrong state token',400))
        response.headers['content-type'] = 'application/json'
        return response
    access_token = request.data

    #upgrade access token to credentials object
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    #get info in json format
    data = json.loads(result)
    login_session['name'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['provider'] = 'facebook'
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['name']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['name'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    #revoking access
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['access_token']
    del login_session['facebook_id'] 
    del login_session['name']
    del login_session['email']
    del login_session['picture']
    del login_session['provider']
    return "Successfully logged out"

@app.route('/about')
def aboutRoute():
    return render_template('about.html')

@app.route('/contact')
def contactRoute():
    return render_template('contact.html')

@app.route('/post/<int:post_id>')
def postRoute(post_id):
    post = session.query(Post).get(post_id) 
    return render_template('post.html',post = post)

@app.route('/create',methods = ['GET','POST'])
def createPost():
    if 'name' not in login_session:
        return redirect('/login')    
    if request.method == 'GET':
        return render_template('createPost.html')
    else:
        title = request.form['title']
        subtitle = request.form['subtitle']
        author = request.form['author']
        content = request.form['content']
        user = login_session['user_id']
        post = Post(title= title,subtitle = subtitle, author = author, description= content,user_id = user)
        session.add(post)
        session.commit()
        flash("created post!")
        return redirect(url_for('indexRoute'))

@app.route('/<int:post_id>/delete',methods=['GET','POST'])
def deletePost(post_id):
    if 'name' not in login_session:
        return redirect('/login')    
    post = session.query(Post).get(post_id)
    if(post.user_id != login_session['user_id']):
        return render_template('noAccess.html')
    if request.method == 'GET':
        return render_template('delete.html',post_id = post_id,post = post)
    else:
        session.delete(post)
        session.commit()
        flash("deleted post!")
        return redirect(url_for('indexRoute'))

@app.route('/<int:post_id>/edit',methods=['GET','POST'])
def editPost(post_id):
    if 'name' not in login_session:
        return redirect('/login')
    post = session.query(Post).get(post_id)
    if(post.user_id != login_session['user_id']):
        return render_template('noAccess.html')
    if request.method == 'GET':
        return render_template('edit.html',post_id = post_id,post = post)
    else:
        title = request.form['title']
        subtitle = request.form['subtitle']
        author = request.form['author']
        content = request.form['content']
        post.title = title
        post.subtitle = subtitle
        post.author = author
        post.description = content
        session.add(post)
        session.commit()
        flash("edited post!")
        return redirect(url_for('indexRoute'))

@app.route('/posts/JSON')
def postsJSON():
    items = session.query(Post).all()
    return jsonify(Posts=[i.serialize for i in items])

@app.route('/posts/<int:post_id>/JSON')
def postJSON(post_id):
    item = session.query(Post).get(post_id)
    return jsonify(Post = [item.serialize])  


if __name__ == '__main__':
    app.secret_key = "my_secret_key"
    app.run(host='0.0.0.0', port=5000)
