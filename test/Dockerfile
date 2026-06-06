FROM lucas42/lucos_scheduled_scripts:latest

COPY test-script.py .
COPY test-interface.py .
RUN pip install requests-mock
RUN echo "* * * * * python test-script.py" | crontab -
