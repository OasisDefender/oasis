# oasis

## Install dependencies
```console
$ pip3.10 install -r requirements.txt
```

## Generate Docker image
```console
$ make
```


## Run on host
```console
$ python3.10 app.py 
 * Serving Flask app 'app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 117-834-075
```


## Run in docker
```console
$ mkdir -p /home/$USER/.db && docker run -d --name oasis --restart always -p 127.0.0.1:5000:5000 -v /home/$USER/.db:/app/db --user $UID:$UID --hostname=$USER@oasis oasis
```


## Usage
Open http://127.0.0.1:5000 in you internet-browser
