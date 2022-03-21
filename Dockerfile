FROM debian:latest

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    gfortran \
    python3-psycopg2

COPY . .

RUN pip install -r requirements.txt

RUN sh compile.sh

CMD [ "python3", "wsgi.py" ]
