import sys
import json
import os
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

os.chmod(command_file, 0o755)
file_name = command_file.split("/")[3]
#os.system("asciinema rec -c \"/root/t2p/run.sh /root/t2p/%s\" /root/t2p/user/recordings/%s/%s" % (command_file, machine_id, file_name))
#os.system("asciicast2gif -w 100 -h 40 /root/t2p/user/recordings/%s/%s /root/t2p/user/recordings/%s/%s.gif" % (machine_id, file_name, machine_id, file_name))
attempt = file_name[-1]
#build_answer(sender, "Attempt: %s/3. Here is your recording." % attempt, "/root/t2p/user/recordings/%s/%s.gif" % (machine_id, file_name))
with open("done/%s.txt" % machine_id, 'w') as f:
	f.write("%s\n" % message_id)
	f.close()
