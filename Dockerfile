FROM ubuntu:22.04

ENV TZ=America/Bahia
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-key adv --keyserver pgp.mit.edu --recv-keys 871920D1991BC93C

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    gfortran \
    python3-psycopg2

COPY . .

RUN pip install -r requirements.txt

RUN sh compile.sh

CMD [ "python3", "wsgi.py" ]
