#!/bin/bash
/usr/sbin/sshd
docker build -t phishing-tools ./kali
docker build -t pentesting-tools ./sql
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000