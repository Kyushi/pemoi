import random
import json
import os

import pytumblr

from flask import flash, \
                  render_template, \
                  redirect, \
                  request, \
                  url_for, \
                  session as login_session, \
                  jsonify

from .database_setup import Category, Item
from .pmoi_db_session import db_session
from config import _basedir

from pemoi import app


t_app_id = json.loads(open(os.path.join(_basedir, 'tumblr_client_secrets.json'), 'r').read())['web']['app-id']
tumblr_client = pytumblr.TumblrRestClient(t_app_id)

class TumblrPost():
    def __init__(self, blog_name, type, post_url, link, post_id, caption, tags):
        self.blog_name = blog_name
        self.post_url = post_url
        self.type = type
        self.link = link
        self.post_id = post_id
        self.caption = caption
        self.tags = tags


def get_tumblr_images(tumblr, limit, offset, tag):
    posts = []
    total_posts = 0
    result = tumblr_client.posts(tumblr, type='photo', limit=limit, offset=offset, tag=tag)
    if 'posts' in result:
        total_posts = result['total_posts']
        for post in result['posts']:
            tumblr_post = TumblrPost(
                post['blog_name'],
                post['type'],
                post['post_url'],
                post['photos'][0]['original_size']['url'],
                post['id'],
                post['photos'][0]['caption'],
                post['tags']
                )
            posts.append(tumblr_post)
    return posts, total_posts

@app.route('/save_tumblr/', methods=['POST'])
def save_tumblr():
    if not 'user_id' in login_session:
        return redirect(url_for('login'))
    if not request.method == 'POST':
        return "This method is not allowed"
    item = Item(
            link=request.form.get('link'),
            title=request.form.get('title'),
            artist='',
            note=request.form.get('note'),
            keywords=request.form.get('keywords'),
            category_id=0,
            user_id=login_session['user_id'],
            public=False
            )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    flash("Item saved succesfully")
    return redirect(url_for('show_item', item_id=item.id))

@app.route('/tumblr/', methods=['GET', 'POST'])
def tumblr():
    if request.method == 'POST':
        tumblr_name = request.form.get('name')
        offset = int(request.form.get('offset'))
        limit = int(request.form.get('n_items', 20))
        tag = request.form.get('tag')
        items, total_posts = get_tumblr_images(tumblr_name, limit, offset, tag)
        if not items:
            flash("No images found")
        return render_template(
            'tumblr.html', 
            items=items, 
            tumblr_name=tumblr_name, 
            offset=offset, 
            limit=limit,
            total_posts=total_posts,
            tag=tag,
            max_post=min(total_posts, offset + limit)
            )
    return render_template('tumblr.html')
