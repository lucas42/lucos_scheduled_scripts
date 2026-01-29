# lucos_scheduled_scripts
A docker base image for python scripts which run on a schedule in the lucOS ecosystem

## Features
* Setting up and running crond
* Ensuring environment variables passed to Docker image are available to cron scripts
* Ensuring the output of cron scripts is piped to the docker logs

## Usage

### Docker

Start your Dockerfile with:
```dockerfile
FROM lucas42/lucos_scheduled_scripts
```

Avoid setting `WORKDIR` or `ENTRYPOINT`

You can set `CMD`, but this is optional.

### Configuring cronjobs

Configure the each job in your Dockerfile using the `crontab` command

For example:
```dockerfile
RUN echo "* * * * * python test-script.py" | crontab -
```

### Using built-in python modules

Needs the following environment variables to be set:

* `SYSTEM` - the code for the system being run (automatically set by lucos_creds)
* `LOGANNE_ENDPOINT` - the URL of a running instance of lucos_loganne
* `SCHEDULE_TRACKER_ENDPOINT` - the URL of a running instance of lucos_schedule_tracker

If using pyenv, add the following to your `Pipfile`:
```
lucos-scheduled-scripts = {file = "/opt/lucos_scheduled_scripts"}
```

Import into your python script as follows:
```python
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

## Testing the base image locally
Run:
```sh
docker compose build && docker compose --profile test up --build test
```
then wait for the next minute to hit for the test cron script to run.