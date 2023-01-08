#!/bin/env python3
#
# Debug wrapper to dump the ticks data structure
#

import sys
from plot.readcsv import readticks

# Handle input file as first arg, or use default filename.
# TODO: make sure file exists
infile="./dave.csv"

if len(sys.argv) > 1:
  infile=sys.argv[1]


# Print for RP and "better", or xx and better
# TODO: validate value
types="RP"
if len(sys.argv) > 2:
  types=sys.argv[2]


ticks = readticks(infile, types)

print (ticks)


