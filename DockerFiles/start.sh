#!/bin/bash 

cd /nginx/app/

python3 myworker.py&
# rq worker --url redis://tv.dresdell.com:6379&
gunicorn -w 4 --bind unix:/nginx/app/app.sock app:app&
