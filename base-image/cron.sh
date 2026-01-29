#!/bin/sh
set -eu

LOG=/var/log/cron.log

# printenv doesn't quote values, which is a problem if one contains a space or newline
# So do some hacky regexes to quote stuff
env -0 | sed 's/"/\\"/g' | sed -z "s/\n/\\\\n/g" | sed 's/\x0/\n/g'| sed 's/=/="/' | sed 's/$/"/g' | sed 's/\\n/\n/g' > .env
[ -p "$LOG" ] || mkfifo "$LOG"
syslogd -n -O /dev/stdout &
exec crond -f -L /dev/stdout

if [ "$#" -gt 0 ]; then
	tail -F "$LOG" &
	exec "$@"
else
	exec tail -F "$LOG"
fi
