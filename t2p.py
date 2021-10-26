from TwitterAPI import TwitterAPI
from pathlib import Path
import subprocess
import json
import os
import re

consumer = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access = os.environ['ACCESS_TOKEN']
secret = os.environ['SECRET_TOKEN']
api = TwitterAPI(consumer, consumer_secret, access, secret)

r = api.request("direct_messages/events/list", {'count':50})
data = json.loads(r.text)
print(data)

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


def process_events(dat):
	for d in dat['events']:
		sender = d['message_create']['sender_id']
		message = d['message_create']['message_data']['text']
		message_id = d['id']
		if(re.match('\/p \d{1,2}\:\:.*', message) is None):
			print("message: %s not applicable" % message)
			continue
		msg_body = message[3:]
		machine_id = msg_body.split("::")[0]
		cmds = msg_body.split("::")[1:]
		commands = ''.join(cmds)
		command_file = get_no(sender, machine_id)
		with open("done/%s.txt" % machine_id) as f:
			if message_id in f.read():
				print("message ID %s already done" % message_id)
				continue
			f.close()
		if(command_file == "user_done"):
			print("user ID %s already done" % sender)
			continue
		with open(command_file, 'w') as f:
			f.write("#!/bin/bash\n\n")
			for cmd in commands.split("%%%"):
				f.write("echo -n \"$ \"\n")
				escaped = cmd.replace('"', '\\"')
				f.write("echo \"%s\" | pv -qL 10 \n" % escaped)
				f.write("%s\n" % cmd)
			f.write("exit\n")
			f.close()

		subprocess.Popen(['screen', '-S', message_id, 'python3', 'record.py', command_file, machine_id, sender, message_id])


process_events(data)
while('next_cursor' in data):
	cur = data['next_cursor']
	r = api.request("direct_messages/events/list", {'count':50, 'cursor':cur})
	data = json_loads(r.text)
	process_events(data)

