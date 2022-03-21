FROM debian:latest

#ENV TZ=America/Bahia
#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#RUN apt-get update && apt-get install -y gnupg1

#RUN gpg --recv-keys AA8E81B4331F7F50 \
    #&& gpg --export AA8E81B4331F7F50| apt-key add -


RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    gfortran \
    python3-psycopg2

COPY . .

RUN pip install -r requirements.txt

RUN sh compile.sh

CMD [ "python3", "wsgi.py" ]
