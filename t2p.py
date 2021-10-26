from TwitterAPI import TwitterAPI
from pathlib import Path
import json
import os
import re

consumer = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access = os.environ['ACCESS_TOKEN']
secret = os.environ['SECRET_TOKEN']
#api = TwitterAPI(consumer, consumer_secret, access, secret)

#r = api.request("direct_messages/events/list")
#data = json.loads(r.text)
data = {'events': [{'type': 'message_create', 'id': '1452997455671402518', 'created_timestamp': '1635256563476', 'message_create': {'target': {'recipient_id': '1452730066190876679'}, 'sender_id': '723792477728157696', 'message_data': {'text': '/p 1:id%%%whoami%%%echo "123"', 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}}}}, {'type': 'message_create', 'id': '1452996366150610955', 'created_timestamp': '1635256303714', 'message_create': {'target': {'recipient_id': '1452730066190876679'}, 'sender_id': '723792477728157696', 'message_data': {'text': '/p 1 id', 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}}}}, {'type': 'message_create', 'id': '1452989134583341069', 'created_timestamp': '1635254579574', 'message_create': {'target': {'recipient_id': '1452730066190876679'}, 'sender_id': '723792477728157696', 'message_data': {'text': 'id%%%echo 1', 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}}}}, {'type': 'message_create', 'id': '1452969425402048517', 'created_timestamp': '1635249880539', 'message_create': {'target': {'recipient_id': '1452730066190876679'}, 'sender_id': '723792477728157696', 'message_data': {'text': '[]{}#%^*+=_\\|~&lt;&gt;$£¥•', 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}}}}, {'type': 'message_create', 'id': '1452740480807092233', 'created_timestamp': '1635195295894', 'message_create': {'target': {'recipient_id': '1452730066190876679'}, 'sender_id': '723792477728157696', 'message_data': {'text': 'jdjdndnd', 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}}}}]}

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
for d in data['events']:
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
	os.system("asciinema rec -c \"/root/t2p/run.sh /root/t2p/%s\" /root/t2p/user/recordings/%s/%s" % (command_file, machine_id, command_file.split("/")[3]))
