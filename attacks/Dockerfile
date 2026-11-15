# Author: Aidan Guenther
FROM kalilinux/kali-rolling
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap hydra sshpass openssh-client curl netcat-openbsd telnet \
    iputils-ping python3 python3-requests python3-paramiko \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /attacks