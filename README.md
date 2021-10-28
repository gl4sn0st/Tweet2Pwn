# Tweet2Pwn

Tweet2Pwn is my little project. It's a bot that allows you to hack virtual machines via Twitter direct messages.
Basically the bot works like this:

1. Bot is webhook(webhook.py) running in webhook.deicide.pl domain, registered in Twitter, waiting for events.
2. After direct message event is received, python script parses the message, gets all required data(like sender id, commands, machine to be hacked id)
3. All commands from user are saved in file user/commands/(machine id)/(user id)_(attempt number)
4. The file also contains echoing pseudo command prompt, for recordings. :)
5. Python script calls subprocess with screen.
6. Inside screen, asciinema(recorder) is run to record the session. After that script run.sh is called.
7. run.sh creates docker container, without internet access, with mounted two files:
* hall of fame html file(so that users can append themselves to it)
* file with commands that user sent to the bot
8. Docker container has ENTRYPOINT set with file containing user commands, so it's run immediately.
9. After running commands, container is closed and removed(--rm flag), recording from asciinema is moved to /var/www/records/json directory so that it can be accessed with https://records.deicide.pl, the player
10. Link to player is generated and sent back to user.


Also, if docker container is running for more than 2 minutes, it's stopped automatically with cron command:

```
docker ps --format="{{.RunningFor}} {{.Image}} {{.ID}}" | grep vulnerable | grep minutes | awk -F: '{if($1>1)print$0}' | awk '{print $4}' | xargs docker stop
```
