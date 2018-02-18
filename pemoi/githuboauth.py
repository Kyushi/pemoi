"""Github OAuth authentication"""

import json
import urllib.request, urllib.parse, urllib.error
import httplib2
import os

from flask import request, \
                  session as login_session, \
                  flash, \
                  redirect, \
                  url_for

from pemoi import app
from .pmoi_auth import get_user_info, get_user_id
from .pmoi_db_session import db_session
from config import _basedir


# Connect with github
@app.route('/githubconnect', methods=['GET', 'POST'])
def githubconnect():
    """Connect with github OAuth API"""

    print("Github info incoming!")
    # Receive state from github
    state = request.args.get('state')
    # If state is not identical to db_session state, return error
    if state != login_session['state']:
        flash("Your state is not my state")
        return redirect(url_for('login'))
    # Code is received from github
    code = request.args.get('code')
    print("We've got a code: %s" % code)
    # Load client id and secret from file
    json_file = os.path.join(_basedir, 'github_client_secrets.json')
    client_id = json.loads(open(json_file, 'r').read())['web']['client_id']
    client_secret = json.loads(open(json_file, 'r').read())['web']['client_secret']
    print("We've got client id and secret: %s, %s" % (client_id, client_secret))
    # Get parameters ready for requesting access token
    params = {'code': code, 'client_id': client_id, 'client_secret': client_secret, 'state':state}
    # Set headers to receive json encoded data
    headers = {'Accept':'application/json'}
    url = 'https://github.com/login/oauth/access_token'
    # Get response with access_token or error from github
    h = httplib2.Http()
    response = h.request(url, 'POST', urllib.parse.urlencode(params), headers=headers)
    print(" Response: ", response)
    # Read the actual result from the response
    result = json.loads(response[1])
    # Let the user know if there was an error
    if 'error' in result:
        flash("There was a problem: %s" % result['error'])
        return redirect('login')
    # get the access token
    access_token = result['access_token']
    #prepare headers with token
    headers = {'Authorization': 'token %s' % access_token}
    # get user data with access_token
    url = 'https://api.github.com/user'
    response, content = h.request(url, 'GET', headers=headers)
    status = response.status
    if status != 200:
        return "There was a problem %s" % json.loads(content)['message']
    result = json.loads(content)
    # Store user data in session
    login_session['provider'] = 'Github'
    login_session['name'] = result['name']
    login_session['picture'] = result['avatar_url']
    login_session['access_token'] = access_token
    # get user e-mail with access_token
    url = 'https://api.github.com/user/emails'
    response, content = h.request(url, 'GET', headers=headers)
    status = response.status
    if status != 200:
        return "There was a problem %s" % json.loads(content)['message']
    # get list of non public e-mail addresses and store them in session
    emails = json.loads(content)
    email_addresses = [e['email'] for e in emails]
    login_session['emails'] = email_addresses
    # Check if user exists in db
    for e in emails:
        user_id = get_user_id(e['email'])
        # If user exists, redirect to index page
        if user_id:
            user = get_user_info(user_id)
            login_session['email'] = e['email']
            login_session['username'] = user.username
            login_session['user_id'] = user_id
            user.picture = login_session['picture']
            db_session.add(user)
            db_session.commit()
            flash("Thanks for logging in, %s" % login_session['username'])
            return redirect('/')
    # If user doesn't exist, redirect to complete signup
    return redirect(url_for('complete_signup'))
