from flask import Flask, request, jsonify
from TwitterAPI import TwitterAPI
from twitterwebhooks import TwitterWebhookAdapter
from pathlib import Path
import base64
import hashlib
import hmac
import subprocess
import json
import os
import re

# Getting needed data to contact twitter api
consumer = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access = os.environ['ACCESS_TOKEN']
secret = os.environ['SECRET_TOKEN']
APP_PATH = "/root/t2p"
AVAILABLE_MACHINES = ['1']
api = TwitterAPI(consumer, consumer_secret, access, secret)

app = Flask(__name__)
events_adapter = TwitterWebhookAdapter(consumer_secret, "/webhooks/twitter", app)

# Function gets ID of bot's account
def get_account_id():
    credentials = api.request('account/verify_credentials').json()
    return credentials['id']
    
BOT_ID = get_account_id()

# I know, this could be done better, but I will do it later :P
def get_no(id, machine):
	if(Path(APP_PATH+"/user/commands/%s/%s_1" % (machine, id)).is_file()):
		if(Path(APP_PATH+"/user/commands/%s/%s_2" % (machine, id)).is_file()):
			if(Path(APP_PATH+"/user/commands/%s/%s_3" % (machine, id)).is_file()):
				if(Path(APP_PATH+"/user/commands/%s/%s_4" % (machine, id)).is_file()):
					if(Path(APP_PATH+"/user/commands/%s/%s_5" % (machine, id)).is_file()):
						return "user_done"
					else:
						return APP_PATH+"/user/commands/%s/%s_5" % (machine, id)
				else:
					return APP_PATH+"/user/commands/%s/%s_4" % (machine, id)
			else:
				return APP_PATH+"/user/commands/%s/%s_3" % (machine, id)
		else:
			return APP_PATH+"/user/commands/%s/%s_2" % (machine, id)
	else:
		return APP_PATH+"/user/commands/%s/%s_1" % (machine, id)

# Function that replaces HTML encoded characters to real characters
def special(cmd):
	rpl = {"&gt;":">", "&lt;":"<", "&amp;":"&"}
	for i in rpl:
		cmd = cmd.replace(i, rpl[i])

	return cmd

# Function sends answer containing "text" to "sender" via API
def answer_text(sender, text):
	event = {
		"event": {
			"type": "message_create",
			"message_create": {
				"target": {
					"recipient_id": sender
				},
				"message_data": {
					"text": text,
				}
			}
		}
	}

	r = api.request("direct_messages/events/new", json.dumps(event))

# Twitter webhook is being tested every 24h for security
@app.route('/webhooks/twitter', methods=['GET'])
def webhook_challenge():
	sha256 = hmac.new(cons.encode(), msg=request.args.get('crc_token').encode(), digestmod=hashlib.sha256).digest()

	resp = {
		'response_token': 'sha256=' + base64.b64encode(sha256).decode()
	}

	return jsonify(response_token="sha256="+base64.b64encode(sha256).decode())

# Here all the interesting stuff is going on, handling DM events :)
@events_adapter.on("direct_message_events")
def handle_message(event_data):
	d = event_data['event']
	sender = d['message_create']['sender_id']
	if(str(sender) == str(BOT_ID)): # If the message is from BOT, don't process it.
		print("Ignoring, message from BOT")
		return
	message = d['message_create']['message_data']['text']
	message_id = d['id']
	if(re.match('\/p \d{1,2}\:\:.*', message) is None): # Message must have required format
		print("message: %s not applicable" % message)
		return
	msg_body = message[3:]
	machine_id = msg_body.split("::")[0]
	cmds = msg_body.split("::")[1:] # All commands from message, after "::"
	commands = ''.join(cmds) # In case someone put "::" in their commands, all elements from list "cmds" are joined
	command_file = get_no(sender, machine_id) # Get path to file where all commands from user will be stored
	if(machine_id not in AVAILABLE_MACHINES):
		print("machine ID %s not available" % machine_id)
		return
	if(command_file == "user_done"): # If user used all their attempts, drop it
		print("user ID %s already done" % sender)
		answer_text(sender, "Maximum number of attempts exceeded. Try again next time.")
		return
	with open(command_file, 'w') as f: # Here all the commands from user are being saved to file
		f.write("#!/bin/bash\n\n")
		for cmd in commands.split("%%%"): # Commands are delimited by "%%%"
			f.write("echo -n \"vulnerable:%s> \"\n" % machine_id) # Pseudo command prompt for recordings ;)
			escaped = cmd.replace("\\", "\\\\").replace('"', '\\"').replace('$', '\$') # Escaping characters
			command = special(escaped)
			ex_command = special(cmd)
			f.write("sleep 1\n") # After every command give user a second to pause the recording
			f.write("echo \"%s\" | pv -qL 10 \n" % command) # Simulate typing a command with pv
			f.write("bash -c \"%s\"\n" % command) # Actually execute the command. "bash -c" is added because in case of errors I don't want the error message to begin with cmds.sh
		f.write("exit\n")
		f.close()
	print("Going with screen for message: %s" % message_id)
	subprocess.Popen(['screen', '-d', '-m', '-S', message_id, 'python3', APP_PATH+'/record.py', command_file, machine_id, sender, message_id]) # Open screen, dont attach to it and run python script record.py inside

# In case someone started typing a message, log it. I just want to know :)
@events_adapter.on("direct_message_indicate_typing_events")
def handle_typing(event_data):
	event = event_data['event']
	id = event['sender_id']
	name = event_data['users'][id]['screen_name']
	print("@%s typed something.." % name)

app.run(port=5555)

