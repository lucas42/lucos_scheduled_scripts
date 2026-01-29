import os, sys, requests
from datetime import datetime

try:
	SYSTEM = os.environ["SYSTEM"]
except KeyError:
	sys.exit("\033[91mSYSTEM environment variable not set\033[0m")
try:
	LOGANNE_ENDPOINT = os.environ["LOGANNE_ENDPOINT"]
except KeyError:
	sys.exit("\033[91mLOGANNE_ENDPOINT environment variable not set - needs to be the URL of a running lucos_loganne instance\033[0m")

session = requests.Session()
session.headers.update({
	"User-Agent": SYSTEM,
	"Content-Type": "application/json",
})

def updateLoganne(type: str, humanReadable: str, url: str = None):
	payload = {
		"type": type,
		"source": SYSTEM,
		"humanReadable": humanReadable,
	}
	if url:
		payload["url"] = url
	try:
		loganne_response = session.post(LOGANNE_ENDPOINT, json=payload)
		loganne_response.raise_for_status()
	except Exception as error:
		print("\033[91m [{}] ** Error calling Loganne: {}\033[0m".format(datetime.now().isoformat(), error), flush=True)