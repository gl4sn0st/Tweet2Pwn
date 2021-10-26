from TwitterAPI import TwitterAPI
from pathlib import Path
import json
import os
import re

consumer = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access = os.environ['ACCESS_TOKEN']
secret = os.environ['SECRET_TOKEN']
api = TwitterAPI(consumer, consumer_secret, access, secret)

#r = api.request("direct_messages/events/list", {'count':50})
#data = json.loads(r.text)
#print(data)
data = {'events': [{'type': 'message_create', 'id': '1453096522414010372', 'created_timestamp': '1635280182828', 'message_create': {'target': {'recipient_id': '1452730066190876679'}, 'sender_id': '723792477728157696', 'message_data': {'text': '/p 3:id%%%whoami%%%echo "siemanko :)"', 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}}}}, {'type': 'message_create', 'id': '1453095696584880135', 'created_timestamp': '1635279985935', 'message_create': {'target': {'recipient_id': '1452730066190876679'}, 'sender_id': '723792477728157696', 'message_data': {'text': 'TEST', 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}}}}]}

def get_no(id, machine):
	if(Path("user/commands/%s/%s_1" % (machine, id)).is_file()):
		if(Path("user/commands/%s/%s_2" % (machine, id)).is_file()):
			if(Path("user/commands/%s/%s_3" % (machine, id)).is_file()):
				
				return "user_done"
			else:
				return "user/commands/%s/%s_3" % (machine, id)
		else:
			return "user/commands/%s/%s_2" % (machine, id)
	else:
		return "user/commands/%s/%s_1" % (machine, id)

def upload_gif(gif):
	file = open(gif, 'rb')
	gif_data = file.read()
	up = api.request("media/upload", None, {'media': gif_data})
	d = json.loads(up.text)
	return d['media_id']

def build_answer(sender, text, gif):
	media_id = upload_gif(gif)
	event = {
		"event": {
			"type": "message_create",
			"message_create": {
				"target": {
					"recipient_id": sender
				},
				"message_data": {
					"text": text,
					"attachment": {
						"type": "media",
						"media": {
							"id": media_id
						}
					}
				}
			}
		}
	}

	r = api.request("direct_messages/events/new", json.dumps(event))

def process_events(dat):
	for d in dat['events']:
		sender = d['message_create']['sender_id']
		message = d['message_create']['message_data']['text']
		if(re.match('\/p \d{1,2}\:.*', message) is None):
			print("message: %s not applicable" % message)
			continue
		msg_body = message[3:]
		machine_id = msg_body.split(":")[0]
		commands = msg_body.split(":")[1]
		command_file = get_no(sender, machine_id)
		if(command_file == "user_done"):
			print("user already done")
			continue
		with open(command_file, 'w') as f:
			f.write("#!/bin/bash\n\n")
			for cmd in commands.split("%%%"):
				f.write("echo -n \"$ \"\n")
				escaped = cmd.replace('"', '\\"')
				f.write("echo \"%s\" | pv -qL 10 \n" % escaped)
				f.write("%s\n" % cmd)
			f.write("exit\n")
		os.chmod(command_file, 0o755)
		file_name = command_file.split("/")[3]
		os.system("asciinema rec -c \"/root/t2p/run.sh /root/t2p/%s\" /root/t2p/user/recordings/%s/%s" % (command_file, machine_id, file_name))
		os.system("asciicast2gif -w 100 -h 40 /root/t2p/user/recordings/%s/%s /root/t2p/user/recordings/%s/%s.gif" % (machine_id, file_name, machine_id, file_name))

		build_answer(sender, "Here is your recording.", "/root/t2p/user/recordings/%s/%s.gif" % (machine_id, file_name))


process_events(data)
while('next_cursor' in data):
	cur = data['next_cursor']
	r = api.request("direct_messages/events/list", {'count':50, 'cursor':cur})
	data = json_loads(r.text)
	process_events(data)

