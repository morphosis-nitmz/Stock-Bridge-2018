import subprocess
import time


while True:
    process = subprocess.check_output('python manage.py runcrons', shell=True)
    time.sleep(250)
