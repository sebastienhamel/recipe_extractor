#ARG DATABASE_URL
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \ 
    python3-venv \
    gettext

WORKDIR /opt/app

# install mysql-server
RUN apt install mysql-server -y

# create venv and installs requirements
COPY requirements.txt /opt/app/requirements.txt
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt
  
RUN usermod -d /var/lib/mysql mysql    

# copy scripts
COPY . /opt/app
COPY mysql-init.sql /docker-entrypoint-initdb.d/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 3306

CMD ["/entrypoint.sh"]
