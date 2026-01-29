#!/bin/sh
set -eu

# printenv doesn't quote values, which is a problem if one contains a space or newline
# So do some hacky regexes to quote stuff
env -0 | sed 's/"/\\"/g' | sed -z "s/\n/\\\\n/g" | sed 's/\x0/\n/g'| sed 's/=/="/' | sed 's/$/"/g' | sed 's/\\n/\n/g' > .env
syslogd -n -O /dev/stdout &

if [ "$#" -gt 0 ]; then
	crond -L /dev/stdout
	exec "$@"
else
	exec crond -f -L /dev/stdout
fi
