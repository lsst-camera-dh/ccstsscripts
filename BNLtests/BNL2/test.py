#!/usr/bin/env python
import os

try:
    st = os.stat("tst")
    print st
except:
    print "no file"
