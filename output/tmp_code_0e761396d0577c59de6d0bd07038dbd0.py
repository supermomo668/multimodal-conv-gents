import os, subprocess, sys
import time

harry_potter = subprocess.Popen(['python', 'harry_potter.py'], stdout=subprocess.PIPE)
iron_man = subprocess.Popen(['python', 'iron_man.py'], stdout=subprocess.PIPE)
darth_vader = subprocess.Popen(['python', 'darth_vader.py'], stdout=subprocess.PIPE)
alan_turing = subprocess.Popen(['python', 'alan_turing.py'], stdout=subprocess.PIPE)
albert_einstein = subprocess.Popen(['python', 'albert_einstein.py'], stdout=subprocess.PIPE)
djingis_khan = subprocess.Popen(['python', 'djingis_khan.py'], stdout=subprocess.PIPE)

while True:
    time.sleep(1)
    for process in [harry_potter, iron_man, darth_vader, alan_turing, albert_einstein, djingis_khan]:
        if process.poll() is not None:
            print(process.stdout.read().decode('utf-8'))
            process = subprocess.Popen(['python', process.args[1]], stdout=subprocess.PIPE)