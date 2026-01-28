FROM python:3.14.2-alpine
WORKDIR /usr/src/app

# Default version of sed in alpine isn't the full GNU one, so install that
RUN apk add sed

COPY cron.sh .

ENTRYPOINT [ "./cron.sh" ]