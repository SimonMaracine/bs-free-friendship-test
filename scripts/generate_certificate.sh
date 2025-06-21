#! /usr/bin/bash

# https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https

openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
