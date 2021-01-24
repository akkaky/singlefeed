FROM python:3.9

ADD . /singlefeed
WORKDIR /singlefeed
RUN python3 -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN chmod +x ./run.sh
ENTRYPOINT ["./run.sh"]
