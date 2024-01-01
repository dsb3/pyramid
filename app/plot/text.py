#!/bin/env python3
#
# Generate Horst training pyramids in text/graph format
#
# Graphs Top Rope, Lead, Down Climb, Down Lead (or others)
# Reads from $1 (will default to "ticks.csv" in current directory)
#
#
# INPUT FILE -- expected data structure is CSV format with
# headers.
#
# Headers are expected to be:
# Date, Grade, Rope, Attempt, with anything else ignored.
#
# If Rope is not set we use a generic "Cx" for "Climbing"
# If Ascent is not set we use "RP" to assume redpoint
#

import sys
import re
import csv

from datetime import datetime


# Import our cfg variables (definitions of rope types, grades, etc)
from plot.cfg import abbrev, validrope, \
        validyds, validboulder, validewbank, validsport, validgrades

from plot.readcsv import readticks, count_pyr



# pyramid will print graphs based on "file"
#

def pyramid(file = "ticks.csv", show = "RP"):

  # Call our function to turn the CSV file into ticks() data structure
  ticks = readticks(file, show)

  # If we got a string, return it as our error message
  if isinstance(ticks, str):
     return "<pre>" + ticks


  # Regardless of validrope, we now calculate usedrope that contains
  # only those rope types we actually have data for.
  usedrope = []

  # delete any that don't have data present
  for rope in ticks.keys():
    count = 0
    try:
      for grade in ticks[rope].keys():
        count += len (ticks[rope][grade])
    except KeyError:
      pass
  
    # No counted ticks for the rope
    if (count > 0):
      usedrope.append(rope)

  # TODO: I just edited the above to count only those ropes which are
  # valid, instead of filtering validropes to remove those not seen.  This
  # means we lost the inherant sorting of rope types, and should now resort
  # the data so (e.g.) the highest grade seen on a rope sorts first.

  
  # CSV data is now loaded into structure, ready to graph.
  outbuffer = "<pre>"
  outbuffer += "Printing pyramids in %s for ascents in %s\n" % (file, show)

  
  
  # Output format
  #
  # Start printing pyramids at the highest grade ticked, plus one.
  #
  #               [ ]                  ...
  #             [ ] [ ]                ...
  #         [ ] [ ] [ ] [ ]            ...
  # [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]    ...
  #
  # [X] is a climb
  # [+] is a cascaded tick from above
  # [ ] is a missing tick
  #
  # Vertical columns plot each rope that's used.  Relative positions of
  # graphs side by side demonstrate discrepancy between abilities.
  #
  #
  
  
  
  # Iterate top down through validgrades.  For each grade, if we have a tick
  # for either that grade, or the one below, we start printing pyramids.  If
  # we don't have a tick for either TR/L then we print a blank space, not an
  # empty pyramid
  # 
  
  # flag to indicate we're starting to print pyramids
  print_row = 0 
  print_for = {}

  for rope in usedrope:
    print_for[rope] = 0;
 
  # Pyramid is 4 rows high, so can't start below 4th rung
  #
  # We need grade as an index into validgrades more often than we need "grade",
  # the textual equivalent
  
  for gradei in reversed(range( 3, len(validgrades))):
    grade=validgrades[gradei]
  
    # From top down, when I find data for either rope, I start printing all
    for rope in usedrope:
      if len( ticks[rope][validgrades[gradei-1]]) > 0 or len( ticks[rope][validgrades[gradei]]) > 0:
        print_row = 1
        print_for[rope] = 1
  
  
    # Nothing found yet?  Or both sets ended, then skip this grade
    if not print_row:
      continue
  
  
    # gather row data for all usedrope.
    pyr={}
    for rope in usedrope:
      pyr[rope]=count_pyr(ticks, show, rope, grade)
  
  
  
    # Header, if we have data in the top two rows
    outbuffer += "\n"
    for rope in usedrope:
      if print_for[rope] > 0:
        # TODO: update header to prepend "5." for YDS grades only
        header="Pyramid for %s %s" % ( abbrev[rope], grade)
        outbuffer += " gr( ##) {:^32} ".format(header)
      else:
        header=""
        outbuffer += "         {:^32} ".format(header)
    outbuffer += "\n"
  
    # print pyramid, row by row
    for i in range(0, 4):
      # row length is 1, 2, 4, 8 (or 2**j)
      for rope in usedrope:
        filled=pyr[rope]["filled"][i]
        flowed=pyr[rope]["flowed"][i]
        empty=pyr[rope]["empty"][i]
        # empty=0
  
        # we might not be printing 
        if print_for[rope] > 0:
          boxes="[X] "*filled + "[+] "*flowed + "[ ] "*empty
        else:
          boxes=""
  
        # Squelch row prefix if not printing
        if print_for[rope] > 0:
          row_prefix="{:>3}({:3})".format( validgrades[gradei-i], len( ticks[rope][ validgrades[gradei-i] ] ) )
        else:
          row_prefix=""
        
        outbuffer += "{:8} {:^32} ".format( row_prefix, boxes )
      outbuffer += "\n"
  
  
  
  
  return outbuffer

