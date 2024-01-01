#!/bin/env python3
#
# Generate Horst training pyramids
#

import sys
from plot.graph import one_svg


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


# defaults to generate a graph
rope="TR"
if len(sys.argv) > 3:
  rope=sys.argv[3]

grade="11c"
if len(sys.argv) > 4:
  grade=sys.argv[4]

print( one_svg(file = infile, show = types, rope=rope, grade=grade) )


