#!/usr/bin/python3

import subprocess as proc
import logging as log
import os
from signal import SIGKILL
from time import sleep

log.basicConfig(level=log.INFO if 'DEBUG' in os.environ else log.WARNING,
                format='%(asctime)s - %(levelname)s - %(message)s')

PROC_NAME = 'skypeforlinux'
INTERVAL = 60 * 30  # minutes


def proc_lookup(procname):
    pids = []
    p = proc.Popen(['ps', '-A'], stdout=proc.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        if procname in line.decode():
            pid = int(line.split(None, 1)[0])
            pids.append(pid)

    return pids


def main():
    while True:
        sleep(INTERVAL)
        log.info('Initiating proc_lookup')
        pids = proc_lookup(PROC_NAME)
        if pids:
            pid = pids[0]
            log.info("Sending sigkill to %s:%s" % (PROC_NAME, pid))
            os.kill(pid, SIGKILL)
            sleep(0.5)
            devnull = open(os.devnull, 'w')
            log.info('Launching %s' % PROC_NAME)
            proc.Popen(PROC_NAME, stdout=devnull, stderr=proc.STDOUT)
        else:
            log.info('No process %s found, going to sleep...' % PROC_NAME)


if __name__ == '__main__':
    log.info('Starting skype reloader')
    main()
