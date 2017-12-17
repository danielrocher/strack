#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017

import re

def removeRegEx(line):
    line=re.sub(r'(\^|\$)', '',line)
    line=line.replace("\\.",".").replace(".*","*")
    return line

def escapeRegEx(line):
    line=line.replace('.', '\\.').replace('*', '.*')
    line="^"+line+"$"
    return line


