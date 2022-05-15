import psutil
import sys
import time
import subprocess


BEEP = "beep -f 1000 -n -f 2000 -n -f 1500"


def process_count(proc_name):
    process_poll = []
    for proc in psutil.process_iter():
        if proc_name in proc.name():
            process_poll.append(proc.pid)
    return len(process_poll)
            

def main():

    name = sys.argv[1]
    limit = sys.argv[2]

    while True:
        if process_count(name) < int(limit):
            subprocess.run(BEEP.split(' '))
        time.sleep(3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
