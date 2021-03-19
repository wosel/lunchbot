FROM python:3.6

ADD requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
RUN mkdir -p src
ADD lunchbot.py /src
ADD pubs.py /src
ADD config.json /src
ADD run.sh /src
RUN chmod a+x /src/run.sh
WORKDIR /


ENTRYPOINT ["./src/run.sh"]
