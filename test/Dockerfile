FROM lucas42/lucos_scheduled_scripts

COPY test-script.py .
RUN echo "* * * * * python test-script.py" | crontab -
