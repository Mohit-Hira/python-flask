from flask import *
from google.cloud import storage, datastore
import google.oauth2.id_token
from google.auth.transport import requests

from datetime import date,datetime

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './key/calendar2-383716-5c52ee4739af.json'


app = Flask(__name__,  static_folder='static')
storage_client = storage.Client()
client = datastore.Client()
firebase_request_adapter = requests.Request()
app.secret_key = 'super secret key'

bucket_name = 'instagram_details'

def generate_blob_name(filename):
    import uuid
    return f'{str(uuid.uuid4())}.{filename.rsplit(".", 1)[1]}'


def store_time(email, dt):
    entity = datastore.Entity(key = client.key('User', email, 'visit'))
    entity.update({'timestamp' : dt})
    client.put(entity)

def fetch_times(email, limit):
 ancestor_key = client.key('User', email)
 query = client.query(kind='visit', ancestor=ancestor_key)
 query.order = ['-timestamp']
 times = query.fetch(limit=limit)
 return times

def viewPosts():
    query = client.query(kind='posts')
    query.add_filter('userid', '=', session['userid'])
    query.order = ['-created_at']
    data = list(query.fetch())
    return data

def viewPostsHome():
    queryx = client.query(kind='users')
    queryx.add_filter('userid', '=', session['userid'])
    result = list(queryx.fetch())
    query = client.query(kind='posts')
    mainData = []
    for items in result[0]['following']:
        query.add_filter('userid', '=',items)
        query.order = ['-created_at']
        data = list(query.fetch())
        # print(data)
        # print('----------------')
        # mainData.append(data)
        for item in data:
            mainData.append(item)
    querydesr = client.query(kind = 'posts')
    querydesr.add_filter('userid', '=', session['userid'])
    resultdesr = list(querydesr.fetch())
    for item in resultdesr:
        mainData.append(item)
    return mainData



@app.route('/')
def root():
    # session.pop('userid', None)
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            store_time(claims['email'], datetime.now())
            times = fetch_times(claims['email'], 10)
            print (claims)
            userid = claims['email']
            password = "pass"
            query = client.query(kind='users')
            query.add_filter('userid', '=', userid)
            existing_user = list(query.fetch())
            if existing_user:
                print("user exists!!")
            else:
                entity = datastore.Entity(key=client.key('users'))
                entity.update({
                'username': claims['name'],
                'userid': userid,
                'password': password,
                'followers': [

                ],
                'following' : [

                ]
            })
                client.put(entity)
            session['userid'] = claims['email']
            session['username'] = claims['name']
            print(session)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('index.html', user_data=claims, times=times, error_message=error_message)


@app.route('/signout', methods = ['POST', 'GET'])
def signout():
    session.clear()
    temp = session['userid']
    session.pop('userid', None)
    session.pop('username', None)
    return redirect(url_for('root'))


@app.route('/loggedin')
def loggedin():
    if not session:
        return redirect(url_for('root'))
    else:
        data = viewPostsHome()
        return render_template('logged-in.html', userid = session["userid"], username = session['username'], data = data)
        

@app.route('/viewProfile')    
def viewProfile():
    if not session:
        return redirect(url_for('root'))
    else:
        query29 = client.query(kind = 'users')
        query29.add_filter('userid', '=', session['userid'])
        resultxe = list(query29.fetch())
        followersCount = len(resultxe[0]['followers'])
        followingCount = len(resultxe[0]['following'])
        data = viewPosts()
        postCount = len(data)
        return render_template('user_profile.html', userid = session['userid'], username = session['username'], data = data, followersCount = followersCount, followingCount = followingCount,postCount=postCount)


@app.route('/viewFollowers/<userid>')
def viewFollowers(userid):
    query = client.query(kind='users')
    query.add_filter('userid', '=', userid)
    result = list(query.fetch())
    followers = result[0]['followers']
    return render_template('followers.html',followers = followers, userid = userid)

@app.route('/viewFollowing/<userid>')
def viewFollowing(userid):
    query = client.query(kind='users')
    query.add_filter('userid', '=', userid)
    result = list(query.fetch())
    following = result[0]['following']
    return render_template('following.html',following = following, userid = userid)

@app.route('/followUser/<userid>')
def followUser(userid):
    query2 = client.query(kind = 'users')
    query2.add_filter('userid', '=', userid)
    resultx = list(query2.fetch())
    username = resultx[0]['username']
    followersCount = len(resultx[0]['followers'])
    followingCount = len(resultx[0]['following'])
    querys = client.query(kind='posts')
    querys.add_filter('userid', '=', userid)
    querys.order = ['-created_at']
    data = list(querys.fetch())

    query = client.query(kind='users')
    query.add_filter('userid', '=', session['userid'])
    result = list(query.fetch())
    event = result[0]
    print(event)
    if (userid in event['following'] ):
        print("done")
    else:
    #     event['following'].insert(0, userid)
    #     client.put(event)
    # # --------------
    # queryb = client.query(kind='users')
    # queryb.add_filter('userid', '=', userid)
    # resultsty = list(queryb.fetch())
    # eventx = resultsty[0]
    # print(eventx)
    # if(session['userid'] in event['followers']):
    #     print("done")
    # else:
    #     eventx['followers'].insert(0, session['userid'])
    #     client.put(eventx)
    query29 = client.query(kind = 'users')
    query29.add_filter('userid', '=', userid)
    resultxe = list(query29.fetch())
    followersCount = len(resultxe[0]['followers'])
    followingCount = len(resultxe[0]['following'])
    postCount = len(data)
    return render_template('afterFollow.html', userid = userid, username = username, data = data,followersCount = followersCount,followingCount = followingCount,postCount = postCount)

@app.route('/unfollowUser/<userid>')
def unfollowUser(userid):
    query = client.query(kind='users')
    query.add_filter('userid', '=', session['userid'])
    result = list(query.fetch())
    event = result[0]
    print(event)
    event['following'].remove(userid)
    client.put(event)
    # -------------------
    queryb = client.query(kind='users')
    queryb.add_filter('userid', '=', userid)
    resultste = list(queryb.fetch())
    eventx = resultste[0]
    print(eventx)
    eventx['followers'].remove(session['userid'])
    client.put(eventx)
    return redirect(url_for('viewProfileUser', userid = userid))
    

@app.route('/viewProfileUser/<userid>')
def viewProfileUser(userid):
    if not session:
        return redirect(url_for('root'))
    else:
        query2 = client.query(kind = 'users')
        query2.add_filter('userid', '=', userid)
        result = list(query2.fetch())
        username = result[0]['username']
        followersCount = len(result[0]['followers'])
        followingCount = len(result[0]['following'])
        print(result[0]['followers'])
        if (session['userid'] in result[0]['followers']):
            isfollowing = True
        else:
            isfollowing = None
        query = client.query(kind='posts')
        query.add_filter('userid', '=', userid)
        query.order = ['-created_at']
        data = list(query.fetch())
        if (userid == session['userid']):
            return redirect(url_for('viewProfile'))
        else:
            postCount = len(data)
            return render_template('other_user.html', userid = userid, username = username, data = data, isfollowing = isfollowing, followersCount = followersCount, followingCount = followingCount,postCount=postCount)

@app.route('/createPost', methods=['GET', 'POST'])
def createPost():
    if(not session['userid']):
        return redirect('root')
    else:
        if request.method == 'POST':
            # Get the uploaded file and caption text
            image = request.files['file']
            caption = request.form['caption']

            # Ensure the file is a PNG or JPG image
            if image.mimetype not in ['image/png', 'image/jpeg']:
                return 'Invalid file type', 400

            # Upload the image to Cloud Storage
            # blob_name = str(uuid.uuid4())
            blob_name = generate_blob_name(image.filename)
            blob = storage_client.bucket(bucket_name).blob(blob_name)
            blob.upload_from_file(image)

            # Save the post to Datastore
            mydict1 = {
                'image_url': f'https://storage.googleapis.com/{bucket_name}/{blob_name}',
                'caption': caption,
                'userid': session['userid'],
                'comments': [
                ],
                'created_at': datetime.now()
               }
            entity = datastore.Entity(key=client.key('posts'))
            entity.update(mydict1)
            client.put(entity)
            return redirect(url_for("viewProfile"))
        else:
            return render_template('upload_post.html')

@app.route('/addComment/<post_id>', methods=['POST', 'GET'])
def addComment(post_id):
    comment = request.form['comment']
    post_id = int(post_id)
    key = client.key('posts', post_id)
    query = client.query(kind = 'posts')
    query.add_filter('__key__', '=', key)
    result = list(query.fetch())
    entity = result[0]
    entity['comments'].append(
        {
        "add_time": datetime.now(),
        "comment": comment,
        "comment_by": session['userid']
        }
    )
    client.put(entity)
    return redirect(url_for('loggedin'))

@app.route('/searchUser', methods = ['POST', 'GET'])
def searchUser():
    user = request.form['search']
    query = client.query(kind='users')
    query.add_filter('username', '>=', user)
    result = list(query.fetch())
    return render_template('searchresult.html', query = user, result = result);


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True) 