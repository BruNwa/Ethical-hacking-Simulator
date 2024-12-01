FROM ubuntu:22.04


ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update && apt-get install -y \
    mysql-client \
    nmap \
    netcat \
    curl \
    wget \
    python3 \
    python3-pip \
    git \
    vim \
    openssl \
    iputils-ping \
    net-tools \
    dnsutils \
    telnet \
    && rm -rf /var/lib/apt/lists/*


RUN pip3 install --no-cache-dir \
    requests \
    pymysql \
    cryptography


WORKDIR /workspace



CMD ["tail", "-f", "/dev/null"]