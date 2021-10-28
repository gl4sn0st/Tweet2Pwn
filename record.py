import sys
import json
import os
import subprocess
import re
from TwitterAPI import TwitterAPI

consumer = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access = os.environ['ACCESS_TOKEN']
secret = os.environ['SECRET_TOKEN']
api = TwitterAPI(consumer, consumer_secret, access, secret)

command_file = sys.argv[1]
machine_id = sys.argv[2]
sender = sys.argv[3]
message_id = sys.argv[4]

def upload_gif(gif):
	file = open(gif, 'rb')
	gif_data = file.read()
	up = api.request("media/upload", None, {'media': gif_data})
	d = json.loads(up.text)
	return d['media_id']

def build_answer(sender, text):
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

os.chmod(command_file, 0o755)
file_name = command_file.split("/")[-1]
c = '"/root/t2p/run.sh \"%s\" \"%s\""' % (command_file, machine_id)
r = '/root/t2p/user/recordings/%s/%s' % (machine_id, file_name)
#os.system("asciinema rec -c \"/root/t2p/run.sh %s %s\" /root/t2p/user/recordings/%s/%s" % (command_file, machine_id, machine_id, file_name))
#os.system("asciicast2gif -w 100 -h 40 /root/t2p/user/recordings/%s/%s /root/t2p/user/recordings/%s/%s.gif" % (machine_id, file_name, machine_id, file_name))
cmd_data = subprocess.check_output("/usr/bin/asciinema rec -c \"/root/t2p/run.sh %s %s\" /var/www/records/json/%s" % (command_file, machine_id, message_id), shell=True)
#link = re.search(r'(http[^\\]+)\\n', str(cmd_data)).groups()[0]
link = "https://records.deicide.pl/index.php?msgid=%s" % message_id
attempt = file_name[-1]
if(os.path.getsize("/var/www/records/json/%s" % message_id) > 50000000):
	here = "Here is your recording. WARNING: It's over 50MB. Consider changing your commands."
else:
	here = "Here is your recording."
build_answer(sender, "Attempt: %s/5. %s\n\n%s" % (attempt, here, link))
