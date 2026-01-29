# lucos_scheduled_scripts
A docker base image for python scripts which run on a schedule in the lucOS ecosystem

## Features
* Setting up and running crond
* Ensuring environment variables passed to Docker image are available to cron scripts
* Ensuring the output of cron scripts is piped to the docker logs

## Usage

### Docker

Start your Dockerfile with:
```
FROM lucas42/lucos_scheduled_scripts
```

Avoid setting `WORKDIR` or `ENTRYPOINT`

You can set `CMD`, but this is optional.

### Configuring cronjobs

Pipe the output of any cronjobs to `/var/log/cron.log` in order for it to appear in the docker image's logs.

For example:
```
RUN echo "* * * * * python test-script.py >> /var/log/cron.log 2>&1" | crontab -
```

### Using built-in python modules

Needs the following environment variables to be set:

* `SYSTEM` - the code for the system being run (automatically set by lucos_creds)
* `LOGANNE_ENDPOINT` - the URL of a running instance of lucos_loganne
* `SCHEDULE_TRACKER_ENDPOINT` - the URL of a running instance of lucos_schedule_tracker

Import into your python script as follows:
```
from loganne import updateLoganne
from schedule_tracker import updateScheduleTracker
```

`updateLoganne` takes the following parameters:

* **`type`** - The type of event being logged
* **`humanReadable`** - A description of the event which humans can easily understand
* **`url`** - A link to a human-readable page regarding the item which the event pertains to (**not** an API endpoint)

`updateScheduleTracker` takes the following parameters:

* **`success`** - A boolean indicating whether the job completed sucessfully
* **`system`** - The scheduled job being run.  Defaults to the `SYSTEM` environment variable, but should be set to something unique on systems with multiple scheduled jobs.
* **`message`** - An error message indicating why the job failed.  Not applicable when `success` is True.
* **`frequency`** - A postive integer specifying how often the job is scheduled to run, in seconds.  Defaults to 1 day.