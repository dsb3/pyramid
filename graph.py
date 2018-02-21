#!/bin/env python3
#
# Generate Horst training pyramids
#

import sys
from plot.text import pyramid as text_pyramid


# Handle input file as first arg, or default to "./ticks.csv"
# TODO: make sure file exists
infile="./ticks.csv"

if len(sys.argv) > 1:
  infile=sys.argv[1]


# Print for RP and "better", or xx and better
# TODO: validate value
types="RP"
if len(sys.argv) > 2:
  types=sys.argv[2]


print( text_pyramid(file = infile, show = types) )


