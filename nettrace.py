#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2016


__version__="0.1"


import argparse
import sys, time, signal

from include.parsestrace import *
from include.parseprofilefile import *

class Main():
    def __init__(self):
        self.debug=False
        self.argparse_thread=None
        self.profile=False

        # parse arguments
        self.parseArgs()

        # SIGINT for interrupt program
        signal.signal(signal.SIGINT, self.signal_handler)

        dic={}
        if self.profile!=False:
            prf=ParseProfileFile(self.profile)
            dic=prf.getDic()
            if dic==None:
                sys.exit(1)
        print dic
        self.argparse_thread=ParseStrace("454", dic, debug=self.debug, loglevel=4) # TODO Fixme
        self.argparse_thread.start()
        
        while self.argparse_thread:
            time.sleep(1)


    def signal_handler(self, signal, frame):
        self.printDebug("Wait. Stopping all ...")
        self.argparse_thread.stop()
        self.argparse_thread.join()
        self.argparse_thread=None
        

    def printDebug(self, msg):
        if self.debug:
            print(str(msg))

    def parseArgs(self):
        # Parse Args
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--version", help="show version", action="store_true")
        parser.add_argument("-p", "--profile", help="profile file", metavar="FILENAME")
        parser.add_argument("--debug", help="Debug", action="store_true")
        args=parser.parse_args()

        appName=sys.argv[0]
        if args.version==True:
            print ("{0} version : {1}".format(appName, __version__))
            sys.exit()
        if args.debug==True:
            self.debug=True
        if args.profile:
            self.profile=args.profile

    def callbackAlert(self, msg):
        # if log
        if self.log:
            self.my_logger.critical("appFirewall: %s" % msg)




if __name__ == "__main__":
    Main()



