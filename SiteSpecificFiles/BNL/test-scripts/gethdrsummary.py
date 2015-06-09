#!/usr/bin/env python
import hdrtools as ht
import sys

fileName = sys.argv[1]
outfl = sys.argv[2]
ht.hdrsummary(fileName,outfl)
