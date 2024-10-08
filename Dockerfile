FROM ubuntu:24.04

# install pip and binaries used by python-ldap
RUN apt update -y && apt install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update -y && \
    apt install -y python3-full python3.12-full libsasl2-dev python3-pip python3.12-dev libldap2-dev libssl-dev libpq-dev && \
    apt clean

COPY ./requirements.txt /app/requirements.txt


WORKDIR /app

RUN python3.12 -m venv .venv && \
    . .venv/bin/activate && \
    pip3 install -r requirements.txt

COPY . /app

ENV FLASK_APP=app.py
ENV AUTHLIB_INSECURE_TRANSPORT=1

ENTRYPOINT [ "uwsgi", "--http-socket", "0.0.0.0:5000", "--processes", "16", "--wsgi-file", "app.py", "--callable", "app","--uid", "www-data", "--log-master"]