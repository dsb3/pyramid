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
from plot.cfg import abbrev, validrope, validascent, \
        validyds, validboulder, validewbank, validfont, validgrades

from plot.readcsv import readticks, count_pyr



# pyramid will print graphs based on "file"
#

def pyramid(file = "ticks.csv", show = "RP"):

  # Call our function to turn the CSV file into ticks() data structure
  ticks = readticks(file, show)

  # If we got a string, return it as our error message
  if isinstance(ticks, str):
     return ticks


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
  outbuffer += "Printing pyramids in %s for ascents in %s\n" % (file, validascent)

  
  
  # Output format
  #
  # highestgrade + 1
  #               [ ]                  ...
  #             [ ] [ ]                ...
  #         [ ] [ ] [ ] [ ]            ...
  # [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]    ...
  #
  # nextgrade
  #               [ ]                  ...
  #             [ ] [ ]                ...
  #         [ ] [ ] [ ] [ ]            ...
  # [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]    ...
  #
  # ...
  # ...
  #
  # Each vertical strip is rope (TR, L) generated separately but
  # aligned by grades.
  #
  # The separation of pyramids is an indication of TR discrepancy.
  #
  # Ticks at each grade are [X]
  # Overflow where excess climbs are cascaded down are [+]
  # Empty boxes are [ ]
  #
  #
  # TODO: for graphics output, graphical distinction for RP, F, OS.
  #       for graphics, shade distinction for newer vs older ticks
  #       e.g. ticks > 3 mo are bright, > 6 mo are dimmer, > 9 are
  #       very faint, and > 12 are grey and look empty
  #
  # Each vertical strip is generated separately.  I want these to line
  # up horizontally, -- the separation between them being an indication of
  # lead to tr discrepancy.
  
  # Overfull grades flow down to empty holes below
  
  
  # TODO:
  # - dynamic graphical output with slider (SVG/javascript can do this?)
  #   to show cumulative data RE + RP + F + OS, or RP + F+ OS, or ....
  #
  
  
  # First draft -- Print text output
  # (deal with graphics later)
  
  
  
  # Iterate top down through validgrades.  For each grade, if we have a tick
  # for either that grade, or the one below, we start printing pyramids.  If
  # we don't have a tick for either TR/L then we print a blank space, not an
  # empty pyramid
  # 
  
  
  print_row=0
  print_for={}
  
  # defaults to zero
  for rope in usedrope:
    print_for[rope]=-1000   # flag never seen
  
  
  # Pyramid is 4 rows high, so can't start below 4th rung
  #
  # We need grade as an index into validgrades more often than we need "grade",
  # the textual equivalent
  
  for gradei in reversed(range( 3, len(validgrades))):
    grade=validgrades[gradei]
  
    # From top down, when I find data for either rope, I start printing all
    for rope in usedrope:
      # only look to start if we've not already done so - this lets decrementing
      # print_for allow us to stop printing rows
      if not print_row:
        if len( ticks[rope][validgrades[gradei-1]]) > 0 or len( ticks[rope][validgrades[gradei]]) > 0:
          print_row = 1
  
      # Separately flag to start printing this rope type, if we've not seen it yet
      if print_for[rope] <= -1000:
        if len( ticks[rope][validgrades[gradei-1]]) > 0 or len( ticks[rope][validgrades[gradei]]) > 0:
          # starting number is how aggressively we stop printing pyramids.
          # -= 3 on any pyrs with all [X]; -= 1 with all [X] or [+]
          print_for[rope] = 4  # xxx 3
  
  
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
  
  
    # analyse row just printed for each rope
    # - full pyramid of ticks means we stop printing more
    # - or, after two full pyramids of ticks with overflow we stop
    #
    # - if the last row in this pyramid contains ONLY overflow ticks
    #   and there aren't real ticks below, then stop very aggressively
    #
    for rope in usedrope:
      nticks = sum( pyr[rope]["filled"] )
      nflows = sum( pyr[rope]["flowed"][:4] )   # discard overflow
  
      if nticks >= 15:
        print_for[rope] -= 2     # -3 since it also counts below
  
      if nticks + nflows >= 15:
        print_for[rope] -= 1
  
      # Count any ticks that are below the last row.  If there are any
      # then keep printing pyramids.  If there are none then we stop
      # at least when the last row is all overflow.
      ticksbelow=0
      i = gradei-4
      while i >= 0:
        ticksbelow += len( ticks[rope][ (validgrades[i]) ] )
        i -= 1
  
      # no ticks below, and fourth row is fully "flow" ticks, then stop
      # very aggressively.
      # TODO: unify these steps, and thresholds
      if ticksbelow == 0 and pyr[rope]["flowed"][3] == 8:
        print_for[rope] -= 10
  
  
    # Did we stop printing for all ropes?  If so, exit our
    # main loop and stop.
    keep_printing=0
    for r in print_for.keys():
      if print_for[r] > 0 or print_for[r] == -1000: 
        keep_printing=1
  
    # break out of the for loop, and exit
    if not keep_printing:
      break
  
  
  return outbuffer

