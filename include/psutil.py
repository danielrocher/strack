#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017

# replace psutil (very light ...)

import os

class Process():
    def __init__(self, pid, name):
        self._name=name
        self.pid=int(pid)

    def name(self):
        return self._name


def pid_exists(pid):
    if os.path.isdir('/proc/{}'.format(pid)):
        return True
    return False


def process_iter():
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    res=[]
    for pid in pids:
        try:
            program=open(os.path.join('/proc', pid, 'comm'), 'rb').read()
            program=program.replace("\n", "").strip()
            c=Process(pid, program)
            res.append(c)
        except IOError:
            continue
    return res



if __name__ == "__main__":
    print pid_exists(1)
    for proc in process_iter():
        print proc.name(), proc.pid

