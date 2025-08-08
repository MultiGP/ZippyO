#!/usr/bin/env python
import gevent
import gevent.monkey
import functools
import ConfigContext
gevent.monkey.patch_all()

import json
import math
import Config
import traceback
from json2html import *     
import re

from flask import Flask, render_template, session,  request, Response
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
app.config['TEMPLATES_AUTO_RELOAD'] = True
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

@app.route('/bracket')
def bracket():
    with open(file_path, "r") as file:
        data = json.load(file)  # Load the file content into a Python object
    file.close()
    return render_template('bracket.html',async_mode=socketio.async_mode,bracket=bracket_json )

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
            check_for_bracket_change(data)
            gevent.sleep(1)
        except Exception as e: 
            gevent.sleep(1)
            error_msg = traceback.format_exc()
            print(f"Caught an exception: {e}")
            print(f"Detailed traceback:\n{error_msg}")

def check_for_bracket_change(data):
    race_info = data["Race"]["Information"]
    if "Bracket" in race_info:
        if "Checkered" in data["Race"]["FlagColor"] :
            finish_order = []
            for driver in data["Drivers"]:
                finish_order.append({"pilot_id":int(driver["LastName"])})
            before = json.dumps(bracket_json)
            update_match(bracket_json, race_info, finish_order)
            after = json.dumps(bracket_json)
            if (before != after):
                print ("bracket changed")
                 
                socketio.emit('bracket_change', bracket_json)
                save_bracket_data()

        if "Green" in data["Race"]["FlagColor"] :
            match = find_match_by_id(bracket_json, race_info)
            before = json.dumps(bracket_json)
            bracket_json["current_bracket_race"] = match["race"]
            bracket_json["last_races_changed"] = []
            after = json.dumps(bracket_json)
            if (before != after):
                print ("bracket changed flags")
                socketio.emit('bracket_change', bracket_json)
                save_bracket_data()
    
def create_double_elim_4p_bracket(pilots):
    #if len(pilots) != 16:
    #    raise ValueError("This bracket requires exactly 16 pilots.")

    bracket = {
        "current_bracket_race": "",
        "last_races_changed": [],
        "winners": [],
        "losers": [],
    }

    # --- Bracket Winners Bracket ---
    # Round 1: 16 pilots -> 4 matches of 4 pilots
    winners_round1 = [
        {
            
            "race" : 1,
            "match_id": "Bracket Winners 1 - 1",
            "pilots": [pilots[2], pilots[5],pilots[10], pilots[13]],
            "advance_to": "Bracket Winners 2 - 1",
            "advance_to_seats": [1,2],
            "drop_to": "Bracket Losers 1 - 1",
            "drop_to_seats": [1,2],
            "advance": [],
            "drop": []
        },
        {
            "race" : 2,
            "match_id": "Bracket Winners 1 - 2",
            "pilots": [pilots[1], pilots[6],pilots[4], pilots[15]],
            "advance_to": "Bracket Winners 2 - 1",
            "advance_to_seats": [3,4],
            "drop_to": "Bracket Losers 1 - 1",
            "drop_to_seats": [3,4],
            "advance": [],
            "drop": []
        },
        {
            "race" : 3,
            "match_id": "Bracket Winners 1 - 3",
            "pilots": [pilots[3], pilots[4],pilots[11], pilots[12]],
            "advance_to": "Bracket Winners 2 - 2",
            "advance_to_seats": [1,2],
            "drop_to": "Bracket Losers 1 - 2",
            "drop_to_seats": [1,2],
            "advance": [],
            "drop": []
        },
        {
            "race" : 4,
            "match_id": "Bracket Winners 1 - 4",
            "pilots": [pilots[0], pilots[7],pilots[8], pilots[15]],
            "advance_to": "Bracket Winners 2 - 2",
            "advance_to_seats": [3,4],
            "drop_to": "Bracket Losers 1 - 2",
            "drop_to_seats": [3,4],
            "advance": [],
            "drop": []
        }
    ]
    bracket["winners"].append(winners_round1)

    # Round 2: 8 advancing pilots -> 2 matches of 4
    winners_round2 = [
        {
            "race" : 6,
            "match_id": "Bracket Winners 2 - 1",
            "pilots": [None]*4,
            "advance_to": "Bracket Winners 3 - 1",
            "advance_to_seats": [1,2],
            "drop_to": "Bracket Losers 2 - 1",
            "drop_to_seats": [3,4],
            "advance": [],
            "drop": []
        },
        {
            "race" : 8,
            "match_id": "Bracket Winners 2 - 2}",
            "pilots": [None]*4,
            "advance_to": "Bracket Winners 3 - 1",
            "advance_to_seats": [3,4],
            "drop_to": "Bracket Losers 2 - 2",
            "drop_to_seats": [3,4],
            "advance": [],
            "drop": []
        }
    ]
    bracket["winners"].append(winners_round2)

    # Round 3 (Bracket Winners Final): 4 advancing pilots -> 1 match of 4
    winners_final = [
        {
            "race" : 11,
            "match_id": "Bracket Winners 3 - 1",
            "pilots": [None]*4,
            "advance_to": "Bracket Winners 4 - 1",
            "advance_to_seats": [1,2],
            "drop_to": "Bracket Losers 4 - 1",
            "drop_to_seats": [1,2],
            "advance": [],
            "drop": []
        }
    ]
    bracket["winners"].append(winners_final)

    winners_final = [
        {
            "race" : 14,
            "match_id": "Bracket Winners 4 - 1",
            "pilots": [None]*4,
            "advance": [],
            "drop": []
        }
    ]
    bracket["winners"].append(winners_final)
    # --- Bracket Losers Bracket ---
    # Bracket Losers Round 1: 8 pilots dropped from Bracket Winners  -> 2 matches of 4
    losers_round1 = [
        {
            "race" : 5,
            "match_id": "Bracket Losers  1 - 1",
            "pilots": [None]*4,
            "advance_to": "Bracket Losers 2 - 1",
            "advance_to_seats": [1,2],
            "advance": [],
            "eliminate": []
        },
        {
            "race" : 7,
            "match_id": "Bracket Losers 1 - 2",
            "pilots": [None]*4,
            "advance_to": "Bracket Losers 2 - 2",
            "advance_to_seats": [1,2],
            "advance": [],
            "eliminate": []
        }
    ]
    bracket["losers"].append(losers_round1)

    # Bracket Losers Round 2: 4 from Bracket Losers  + 4 dropped from Bracket Winners 2 -> 2 matches of 4
    losers_round2 = [
        {
            "race" : 9,
            "match_id": "Bracket Losers 2 - 1",
            "pilots": [None]*4,
            "advance_to": "Bracket Losers 3 - 1",
            "advance_to_seats": [1,2],
            "advance": [],
            "eliminate": []
        },
        {
            "race" : 10,
            "match_id": "Bracket Losers 2 - 2",
            "pilots": [None]*4,
            "advance_to": "Bracket Losers 3 - 1",
            "advance_to_seats": [3,4],
            "advance": [],
            "eliminate": []
        }
    ]
    bracket["losers"].append(losers_round2)

    losers_final = [
         {
            "race" : 12,
            "match_id": "Bracket Losers 3 - 1",
            "pilots": [None]*4,
            "advance_to": "Bracket Losers 4 - 1",
            "advance_to_seats": [3,4],
            "advance": [],
            "eliminate": []
        }
    ]
    bracket["losers"].append(losers_final)

    losers_final = [
        {
            "race" : 13,
            "match_id": "Bracket Losers 4 - 1",
            "pilots": [None]*4,
            "advance_to": "Bracket Winners 4 - 1",
            "advance_to_seats": [3,4],
            "advance": [],
            "eliminate": []
        }
    ]
    bracket["losers"].append(losers_final)

    return bracket

def find_match_by_id(bracket, match_id):

    characters_to_remove = "()"
    translation_table = str.maketrans("-", " ", characters_to_remove)
    cleaned_match_id = match_id.translate(translation_table)
    parts = cleaned_match_id.split()  # eg ["Bracket" "Winners" "1" "3"]
    bracket_type = parts[1].lower()  # winners/losers
    round_num = int(parts[2])
    match_num = int(parts[3])

    return bracket[bracket_type][round_num - 1][match_num - 1]

def update_match(bracket, match_id, placements):
    match = find_match_by_id(bracket, match_id)
    #print (placements) 
    finalplacements=[]
    # Assign winners and losers
    for aplacment in placements:
        for apilot in pilots:
            if apilot["pilot_id"] == aplacment["pilot_id"]:
                try:
                    finalplacements.append(apilot)
                except Exception as e:
                    print("exception:",match_id,placements,e) 
                try:
                   if apilot["best_time"] > aplacment["best_time"]:
                       apilot["best_time"] = aplacment["best_time"]
                except KeyError:
                    pass 
                break

    last_races_changed = []
    top_two = []
    bottom_two = []
    if len(finalplacements) > 0:
       top_two.append(finalplacements[0]) 
    if len(finalplacements) > 1:
       top_two.append(finalplacements[1])
    if len(finalplacements) > 2:
       bottom_two.append(finalplacements[2])
    if len(finalplacements) > 3:
       bottom_two.append(finalplacements[3]) 
    
    # Advance winners
    if "advance_to" in match:
        match["advance"] = []
        match["advance"].extend(top_two)
        next_match = find_match_by_id(bracket, match["advance_to"])
        if len(finalplacements) > 0:
            next_match["pilots"][match["advance_to_seats"][0]-1] = top_two[0]
        if len(finalplacements) > 1:
            next_match["pilots"][match["advance_to_seats"][1]-1] = top_two[1]
        last_races_changed.append(next_match["race"])

    # Drop losers
    if "drop_to" in match:
        match["drop"] = []
        match["drop"].extend(bottom_two)
        drop_match = find_match_by_id(bracket, match["drop_to"])
        if len(finalplacements) > 2:
            drop_match["pilots"][match["drop_to_seats"][0]-1] = bottom_two[0]
        if len(finalplacements) > 3:
            drop_match["pilots"][match["drop_to_seats"][1]-1] = bottom_two[1]
        last_races_changed.append(next_match["race"])
    else:
        # If no drop_to, they are eliminated
        if "eliminate" in match:
            match["eliminate"] = []
            match["eliminate"].extend(bottom_two)


    bracket["last_races_changed"] = last_races_changed
    bracket["current_bracket_race"] = match["race"] 


pilots = [
    {
        "pilot_id": i+1,
        "name": f"Pilot{i+1}",
        "best_time" : 200000
    }
    for i in range(16)
] 


bracket_path =  ConfigContext.serverconfig.get_item('GENERAL', 'BRACKET_PATH')
try:
    with open(bracket_path, "r") as file:
        bracket_json = json.load(file)  # Load the file content into a Python object
    file.close()
except Exception as e: 
    print (e)
    bracket_json = {}
    pass
if not bracket_json:
    print("no backup bracket data")
    bracket_json = create_double_elim_4p_bracket(pilots)


#update_match(bracket_json, "Bracket Winners 1 - 1", [{"pilot_id":1},{"pilot_id":3,"best_time":33},{"pilot_id":2,"best_time":22},{"pilot_id":4,"best_time":44}])
print(json.dumps(pilots, indent=4))
#print(json.dumps(bracket_json, indent=4))


def save_bracket_data():
    with open(bracket_path, "w") as file:
        json.dump(bracket_json,file,indent=4) 
    file.close()

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
