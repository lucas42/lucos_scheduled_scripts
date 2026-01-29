FROM lucas42/lucos_scheduled_scripts

COPY test-script.py .
RUN echo "* * * * * python test-script.py >> /var/log/cron.log 2>&1" | crontab -
