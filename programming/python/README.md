# installation
Open this directory in terminal.
It is recommended to create a virtual environment for the python application.
To do this execute
``` sh
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
```
Make shure you have python3 and pip uses python3
If you are using a UNIX like system you can use
``` sh
pip install -r requirements.txt
```
If you use an rbp you should use the script which installs required libraries
``` sh
./rbp-install.sh
```
Run the web.py program
``` sh
python web.py
```
