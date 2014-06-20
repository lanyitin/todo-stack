# -*- coding: utf-8 -*-
import json
import os
import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from flask import Flask, request, g, redirect, url_for, \
    render_template, make_response, Response, session, \
    flash
from flask_assets import Environment
from flask_login import LoginManager, login_user, \
    logout_user, current_user, login_required
from .libs.model import Todo, User, Connection
from .libs.facade import Facade
from flask_oauth import OAuth

from .config import DevelopConfig, ProductionConfig

import smtplib
from email.mime.text import MIMEText

oauth = OAuth()

login_manager = LoginManager()

app = Flask(__name__)


if 'STACKTODOS_DEVELOPMENT_ENVIRONMENT' in os.environ:
    print "develop environment"
    app.config.from_object(DevelopConfig)
else:
    app.config.from_object(ProductionConfig)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True, poolclass=QueuePool, pool_size=20, max_overflow=0)
Session = sessionmaker()
Session.configure(bind=engine)  # once engine is available

assets = Environment(app)

login_manager.init_app(app)
login_manager.login_view = "login"

facebook = oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=app.config['SOCIAL_FACEBOOK_KEY'],
    consumer_secret=app.config['SOCIAL_FACEBOOK_SECRET'],
    request_token_params={'scope': 'email'},
)


def todo2dict(todo):
    return {
        "id": todo.id,
        "content": todo.content,
        "priority": todo.priority,
        "order": todo.order,
        "in_trash": todo.in_trash,
        "required_clock": todo.required_clock,
        "extended_clock": todo.extended_clock,
        "consumed_clock": todo.consumed_clock
    }


def todo2json(todo):
    return json.dumps(todo2dict(todo))


app.jinja_env.filters['todo2json'] = todo2json


@app.before_request
def before_request():
    g.db_session = Session()
    g.facade = Facade(session=g.db_session, engine=engine)
    g.user = current_user


@app.after_request
def after_request(response):
    g.db_session.close()
    g.db_session = None
    g.facade = None
    return response


@login_manager.user_loader
def load_user(id):
    return g.db_session.query(User).filter_by(id=id).first()


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(request.args.get("next") or url_for("main"))

    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    registered_user = g.facade.find_user_by_credential(username, password)
    if registered_user is None:
        return redirect(url_for('login'))
    login_user(registered_user)
    return redirect(request.args.get("next") or url_for("main"))


@app.route('/oauth/facebook/', methods=['GET'])
def login_facebook():
    return facebook.authorize(
        callback=url_for(
            'oauth_authorized',
            _external=True,
            next=request.args.get('next') or request.referrer or None,
        )
    )


@app.route('/oauth/facebook/authorized/')
@facebook.authorized_handler
def oauth_authorized(oauth_resp):
    next_url = request.args.get('next') or url_for('main')
    if oauth_resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)
    session['facebook_token'] = (
        oauth_resp['access_token'],
        '',
    )
    resp = facebook.get('/me')
    if resp.status == 200:
        profile = resp.data
        connection = g.db_session.query(Connection).filter_by(
            provider_id='facebook',
            provider_user_id=profile['id']
        ).first()
        if connection is None:
            new_user = g.facade.register(
                'facebook_' + profile['id'],
                '',
                profile['email'],
            )
            connection = Connection()
            connection.user_id = new_user.id
            connection.provider_id = 'facebook'
            connection.provider_user_id = profile['id']
            connection.access_token = oauth_resp['access_token']
            connection.secret = ''
            connection.display_name = profile['name']
            connection.profile_url = profile['link']
            g.db_session.add(connection)
            g.db_session.commit()
            login_user(new_user)
        else:
            user = g.db_session.query(User).filter_by(id=connection.user_id).first()
            login_user(user)
    return redirect(next_url)


@facebook.tokengetter
def get_twitter_token(token=None):
    return session.get('facebook_token')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    g.facade.register(username, password, email)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def main():
    todos = g.facade.find_todos_by_owner(g.user)
    return make_response(
        render_template(
            "display_stack.html",
            stack=todos,
        )
    )


@app.route('/push/', methods=["POST"])
@login_required
def pushItem():
    todos = g.facade.push_todo(
        g.user,
        Todo(
            content=request.json["item"],
            owner=g.user,
            required_clock=request.json["required_clock"],
            priority=request.json["priority"]
        )
    )
    return Response(json.dumps([todo2dict(todos[0])]), mimetype='application/json')


@app.route('/append/', methods=["POST"])
@login_required
def appendItem():
    response = g.facade.push_todo(
        g.user,
        Todo(
            content=request.json["item"],
            owner=g.user,
            required_clock=request.json["required_clock"],
            priority=request.json["priority"]
        )
    )
    response = map(todo2dict, response)
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/moveToTrash/<int:todoid>/', methods=["GET"])
@login_required
def moveToTrash(todoid):
    todos = g.facade.move_todo_to_trash(g.user, g.facade.find_todo_by_id(todoid))
    if todos is not None:
        return Response(
            json.dumps([todo2dict(todos[0])]),
            mimetype='application/json',
        )


@app.route('/moveItem/<int:fromIndex>/<int:toIndex>/', methods=["GET"])
@login_required
def moveItem(fromIndex, toIndex):
    g.facade.move_todo(g.user, fromOrder=fromIndex, toOrder=toIndex)
    response = g.facade.find_todos_by_owner(g.user)
    response = map(todo2dict, response)
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/removeItem/<int:todoid>/', methods=["GET"])
@login_required
def removeItem(todoid):
    todos = g.facade.remove_todo(g.user, g.facade.find_todo_by_id(todoid))
    return Response(json.dumps([todo2dict(todos[0])]), mimetype='application/json')


@app.route('/clean_trash/', methods=["GET"])
@login_required
def cleanTrash():
    response = g.facade.clean_trash(g.user)
    response = map(todo2dict, response)
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/raisePriority/<int:todoid>/', methods=["GET"])
@login_required
def raisePriority(todoid):
    todos = g.facade.raise_priority(g.user, g.facade.find_todo_by_id(todoid))
    return Response(json.dumps([todo2dict(todos[0])]), mimetype='application/json')


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    traceback.print_exc()
    response = Response(json.dumps({'message': error.message, 'args': list(error.args)}), mimetype='application/json')
    response.status_code = 500

    msg = MIMEText(unicode(error))

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = 'Urgent an exception occured'
    msg['From'] = 'todo-bot@lanyitin.tw'
    msg['To'] = 'lanyitin@gmail.com'

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()

    return response
