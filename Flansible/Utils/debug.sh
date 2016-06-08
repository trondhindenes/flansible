echo kill screens if any
killall screen || true
cd ~/Flansible/Flansible
echo start celery
screen -d -m -s /bin/bash celery worker -A app.celery --loglevel=info
echo start flower
screen -d -m -s /bin/bash flower --broker=amqp://redis://localhost:6379/0
echo start app
screen -d -m -s /bin/bash /usr/bin/python app.py
cd Utils
