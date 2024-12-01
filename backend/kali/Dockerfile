
FROM kalilinux/kali-rolling


ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libaio-dev \
    libncurses6 \
    libmecab2 \
    grep \
    file \
    nmap \
    binutils \
    util-linux \
    netcat-traditional \
    dirb \
    nikto \
    curl \
    whois \
    dnsutils \
    openssl \
    inotify-tools \
    strace \
    ltrace \
    procps \
    net-tools \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


RUN pip3 install flask --break-system-packages


WORKDIR /app


COPY app.py /app/app.py


ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=3000
ENV FLASK_RUN_HOST=0.0.0.0


EXPOSE 3000


CMD ["flask", "run"]