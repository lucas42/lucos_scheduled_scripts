FROM lucas42/lucos_scheduled_scripts:latest

RUN echo "* * * * * echo \"Test Script\" >> /var/log/cron.log 2>&1" | crontab -
