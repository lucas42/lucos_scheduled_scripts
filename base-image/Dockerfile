FROM python:3.14.2-alpine
# Use the root user's home directory for consistency with the working directory that cron jobs get launched with
WORKDIR /root

# Default version of sed in alpine isn't the full GNU one, so install that
RUN apk add sed

COPY cron.sh .

COPY shared-python /opt/lucos_scheduled_scripts
RUN pip install /opt/lucos_scheduled_scripts

ENTRYPOINT [ "./cron.sh" ]