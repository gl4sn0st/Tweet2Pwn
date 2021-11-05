from pathlib import Path

APP_PATH = "/root/t2p"

def get(id, machine, attempts):
	for i in range(1, attempts+1):
		if(Path(APP_PATH+"/user/commands/%s/%s_%s" % (machine, id, i)).is_file()):
			if(i == attempts):
				return "user_done"
			else:
				continue
		else:
			return APP_PATH+"/user/commands/%s/%s_%s" % (machine, id, i)


print(get("295717570", 1, 5))
				
