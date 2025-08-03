#!/usr/bin/env python
import gevent
import gevent.monkey
import functools
import ConfigContext
gevent.monkey.patch_all()

import json
import Config
from json2html import *     
import re

from flask import Flask, render_template, session, request, Response
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

import sys

import argparse

parser = argparse.ArgumentParser(description='Timing Server')
parser.add_argument('--mock', dest='mock', action='store_true', default=False, help="use mock data for testing")
args = parser.parse_args()
ConfigContext = ConfigContext.ConfigContext()

print (sys.platform.lower())

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = "gevent"

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins='*')
heartbeat_thread = None

zippyo_version = {'major': 0, 'minor': 1}
import time
def check_auth(username, password):
    '''Check if a username password combination is valid.'''
    return username == ConfigContext.serverconfig.get_item('SECRETS', 'ADMIN_USERNAME') and password == ConfigContext.serverconfig.get_item('SECRETS', 'ADMIN_PASSWORD')

def authenticate():
    '''Sends a 401 response that enables basic auth.'''
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    if ConfigContext.serverconfig.get_item('SECRETS', 'ADMIN_USERNAME') or \
        ConfigContext.serverconfig.get_item('SECRETS', 'ADMIN_PASSWORD'):
        @functools.wraps(f)
        def decorated_auth(*args, **kwargs):
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()
            return f(*args, **kwargs)
        return decorated_auth
    # allow open access if both ADMIN fields set to empty string:
    @functools.wraps(f)
    def decorated_noauth(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_noauth

def parse_json(data):
    if isinstance(data, (str)):
       return json.loads(data)
    return data

def json_to_html(data, parent_key=""):
    html = ""
    if isinstance(data, dict):  # If value is a dictionary, recurse
        for key, value in data.items():
            element_id = f"{parent_key}_{key}" if parent_key else key
            html += f'<span style="display: flex;"><div>{element_id}:</div><div name="{element_id}">\n'
            html += json_to_html(value, element_id)
            html += "</div></span>\n"
    elif isinstance(data, list):  # If value is a list, iterate
        for index, item in enumerate(data):
            element_id = f"{parent_key}_{index}"
            html += f'<span style="display: flex;"><div>{element_id}:</div><div name="{element_id}">\n'
            html += json_to_html(item, element_id)
            html += "</div></span>\n"
    else:  # Base case: value is a string, number, or boolean
        html += str(data) + "\n"
    return html

def json_to_html_with_ids(data, parent_key=""):
    html = "<div>"
    for key, value in data.items():
        # Create a unique ID based on nesting (e.g., parent_child)
        element_id = f"{parent_key}_{key}" if parent_key else key

        if isinstance(value, dict):  
            # Recursively process nested dict
            html += json_to_html_with_ids(value, element_id)  
        elif isinstance(value, list):
            # Process lists
            for i, item in enumerate(value):
                if isinstance(item, dict):  
                    html += json_to_html_with_ids(item, f"{element_id}_{i}")
        else:
            # Render primitive values
            html += f'<div><strong>{key}:</strong></div>'
            html += f'<div name="{element_id}"><i>{value}</i></div>'
    html += "</div>"
    return html

#@requires_auth
@app.route('/')
def index():
    with open(file_path, "r") as file:
        data = json.load(file)  # Load the file content into a Python object
    file.close()
    html_table = json_to_html(data)

    return render_template('index.html', async_mode=socketio.async_mode, html_table=html_table )

@app.route('/nextup')
def nextup():
    with open(file_path, "r") as file:
        data = json.load(file)  # Load the file content into a Python object
    file.close()
    return render_template('nextup.html', async_mode=socketio.async_mode, data=data)

@app.route('/inprogress')
def inprogress():
    with open(file_path, "r") as file:
        data = json.load(file)  # Load the file content into a Python object
    file.close()
    return render_template('inprogress.html', async_mode=socketio.async_mode, data=data)

@app.route('/results')
def results():
    with open(file_path, "r") as file:
        data = json.load(file)  # Load the file content into a Python object
    file.close()
    return render_template('results.html', async_mode=socketio.async_mode, data=data)

@socketio.on('connect')
def connect_handler():
    print ('connected!!');
    global heartbeat_thread
    if (heartbeat_thread is None):
        heartbeat_thread = gevent.spawn(heartbeat_thread_function)

@socketio.on('disconnect')
def disconnect_handler():
    print ('disconnected!!');

@socketio.on('get_version')
def on_get_version():
    return zippyo_version

def heartbeat_thread_function(): 
    while True:
        try:
            with open(file_path, "r") as file:
               data = json.load(file)  # Load the file content into a Python object
            file.close()
            socketio.emit('heartbeat', data)
            gevent.sleep(0.5)
        except: 
            print ('exception reading file')


def stop_background_threads():
    try:
        stop_shutdown_button_thread()
        global BACKGROUND_THREADS_ENABLED           
        BACKGROUND_THREADS_ENABLED = False
        global HEARTBEAT_THREAD
        if HEARTBEAT_THREAD:
            HEARTBEAT_THREAD.kill(block=True, timeout=0.5)
            HEARTBEAT_THREAD = None
        stop()
    except: 
        print ('exception killing background threads')

file_path =  ConfigContext.serverconfig.get_item('GENERAL', 'FILE_PATH')
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001 ,debug=False)
