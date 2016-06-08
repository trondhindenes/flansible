killall screen
cd ~/Flansible/Flansible
screen -d -m -s /bin/bash celery worker -A app.celery --loglevel=info
screen -d -m -s /bin/bash flower --broker=amqp://redis://localhost:6379/0
screen -d -m -s /bin/bash /usr/bin/python app.py
cd Utils
