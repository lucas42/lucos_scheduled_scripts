FROM lucas42/lucos_scheduled_scripts:latest

COPY test-script.py .
RUN echo "* * * * * cd `pwd` && python test-script.py >> /var/log/cron.log 2>&1" | crontab -
