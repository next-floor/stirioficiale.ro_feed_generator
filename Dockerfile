FROM ubuntu:18.04

RUN mkdir -p /usr/local/stiri_rss

COPY . /usr/local/stiri_rss

WORKDIR /usr/local/stiri_rss

RUN \
    apt update && \
    apt install tzdata && \
    rm -f /etc/localtime && \
    ln -fs /usr/share/zoneinfo/Europe/Bucharest /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt install --no-install-recommends -y python3 python3-pip python3-setuptools && \
    apt clean && \
    pip3 install --no-cache-dir -r requirements.txt -U

EXPOSE 5000

CMD ["python3", "runner.py"]