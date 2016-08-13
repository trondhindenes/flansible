echo kill screens if any
killall screen || true
cd /home/thadmin/flansible/
echo start celery
screen -d -m -s /bin/bash celery worker -A flansible.celery --loglevel=info
echo start flower
screen -d -m -s /bin/bash flower --broker=redis://localhost:6379/0
echo start app
screen -d -m -s /bin/bash /usr/bin/python app.py
cd Utils
