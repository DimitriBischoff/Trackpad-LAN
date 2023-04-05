# Trackpad LAN


## Get IP local

get local ip address from server
Windows+R => cmd => ipconfig
change ip index.html: line 422. '{YOUR_LOCAL_IP}'


## Launch server

```console
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python server.py
```



## Connect
http://{IP_LOCAL}:6660
