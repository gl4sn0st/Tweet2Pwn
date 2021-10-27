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

consumer = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access = os.environ['ACCESS_TOKEN']
secret = os.environ['SECRET_TOKEN']
APP_PATH = "/root/t2p"
AVAILABLE_MACHINES = ['1']
api = TwitterAPI(consumer, consumer_secret, access, secret)

app = Flask(__name__)
events_adapter = TwitterWebhookAdapter(consumer_secret, "/webhooks/twitter", app)

def get_account_id():
    credentials = api.request('account/verify_credentials').json()
    return credentials['id']
    
BOT_ID = get_account_id()

def get_no(id, machine):
	if(Path(APP_PATH+"/user/commands/%s/%s_1" % (machine, id)).is_file()):
		if(Path(APP_PATH+"/user/commands/%s/%s_2" % (machine, id)).is_file()):
			if(Path(APP_PATH+"/user/commands/%s/%s_3" % (machine, id)).is_file()):
				
				return "user_done"
			else:
				return APP_PATH+"/user/commands/%s/%s_3" % (machine, id)
		else:
			return APP_PATH+"/user/commands/%s/%s_2" % (machine, id)
	else:
		return APP_PATH+"/user/commands/%s/%s_1" % (machine, id)

def special(cmd):
	rpl = {"&gt;":">", "&lt;":"<", "&amp;":"&"}
	for i in rpl:
		cmd = cmd.replace(i, rpl[i])

	return cmd

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

@app.route('/webhooks/twitter', methods=['GET'])
def webhook_challenge():
	sha256 = hmac.new(cons.encode(), msg=request.args.get('crc_token').encode(), digestmod=hashlib.sha256).digest()

	resp = {
		'response_token': 'sha256=' + base64.b64encode(sha256).decode()
	}

	return jsonify(response_token="sha256="+base64.b64encode(sha256).decode())

@events_adapter.on("direct_message_events")
def handle_message(event_data):
	d = event_data['event']
	sender = d['message_create']['sender_id']
	if(str(sender) == str(BOT_ID)):
		print("Ignoring, message from BOT")
		return
	message = d['message_create']['message_data']['text']
	message_id = d['id']
	if(re.match('\/p \d{1,2}\:\:.*', message) is None):
		print("message: %s not applicable, sender: %s, bot: %s" % message)
		return
	msg_body = message[3:]
	machine_id = msg_body.split("::")[0]
	cmds = msg_body.split("::")[1:]
	commands = ''.join(cmds)
	command_file = get_no(sender, machine_id)
	if(machine_id not in AVAILABLE_MACHINES):
		print("machine ID %s not available" % machine_id)
		with open(APP_PATH+"/done/%s.txt" % machine_id, "a") as f:
			f.write("%s\n" % message_id)
			f.close()
		return
	with open(APP_PATH+"/done/%s.txt" % machine_id) as f:
		if message_id in f.read():
			print("message ID %s already done" % message_id)
			f.close()
			return
	if(command_file == "user_done"):
		print("user ID %s already done" % sender)
		answer_text(sender, "Maximum number of attempts exceeded. Try again next time.")
		with open(APP_PATH+"/done/%s.txt" % machine_id, "a") as f:
			f.write("%s\n" % message_id)
			f.close()
		return
	with open(command_file, 'w') as f:
		f.write("#!/bin/bash\n\n")
		for cmd in commands.split("%%%"):
			f.write("echo -n \"vulnerable:%s> \"\n" % machine_id)
			escaped = cmd.replace("\\", "\\\\").replace('"', '\\"').replace('$', '\$')
			command = special(escaped)
			ex_command = special(cmd)
			f.write("echo \"%s\" | pv -qL 10 \n" % command)
			f.write("bash -c \"%s\"\n" % command)
		f.write("exit\n")
		f.close()
	with open("/root/t2p/done/%s.txt" % machine_id, 'a') as f:
		f.write("%s\n" % message_id)
		f.close()
	print("Going with screen for message: %s" % message_id)
	subprocess.Popen(['screen', '-d', '-m', '-S', message_id, 'python3', APP_PATH+'/record.py', command_file, machine_id, sender, message_id])

app.run(port=5555)

