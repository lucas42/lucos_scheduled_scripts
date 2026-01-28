# lucos_scheduled_scripts
A docker base image for python scripts which run on a schedule in the lucOS ecosystem

## Features
* Setting up and running crond
* Ensuring environment variables passed to Docker image are available to cron scripts
* Ensuring the output of cron scripts is piped to the docker logs

