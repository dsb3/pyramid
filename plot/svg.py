#!/bin/env python3
#
# Generate Horst training pyramids in SVG format
#
# Prints a single SVG (graphical) pyramid for:
# - file: input file (either fname or fname.csv)
# - show: ascents to show - defaults to "RP"
# - grade: grade to show - no default; expected to be in file
#          (e.g. don't display "V5" for a top-rope file)
# - rope:  rope to show - no default; expected to be in file
# 
#

import sys
import re
import csv

import jinja2

from datetime import datetime


# Import our cfg variables (definitions of rope types, grades, etc)
from plot.cfg import abbrev, validrope, validascent, \
        validyds, validboulder, validewbank, validfont, validgrades

from plot.readcsv import readticks



def one_svg(file = "ticks.csv", show = "RP", rope = "", grade = ""):

  # call function to gather ticks data structure
  ticks = readticks(file, show)

  # If we got a string, return it as our error message
  if isinstance(ticks, str):
     return ticks


  # Look up the grade index for the grade requested
  try:
    gradei = validgrades.index(grade.lower())
  except:
    return "No such grade"


  # If we've requested a rope that wasn't used, error
  if rope not in ticks.keys():
     return "No data found"

  # This is an abbreviated copy of the calculations done for text
  # (there, we generate for all ropes simultaneously)

  # TODO: enhance to capture flash/onsight/redpoint/etc.
  pyr={}
  pyr["filled"]=[0, 0, 0, 0]      # empty four row pyramid for ticks
  pyr["flowed"]=[0, 0, 0, 0, 0]   # empty four row pyramid for surplus flowed from above, with unused fifth row var
  pyr["empty"]=[0, 0, 0, 0]       # empty four row pyramid for empty box count

  
  # Prefill "flowed" for the top row with a count of all climbs "above"
  for i in range(gradei+1, len(validgrades) - 1):
    pyr["flowed"][0] += len( ticks[rope][ (validgrades[i]) ] )

  # iterate over four rows, capturing "filled" from our ticks data
  for i in range(0, 4):
    pyr["filled"][i] = len( ticks[rope][ (validgrades[gradei - i]) ] )

  # iterate again, cascading excess count into "flowed"
  for i in range(0, 4):
    # too many ticks for this row?  overflow to the next row.
    if pyr["filled"][i] > 2**i:
      pyr["flowed"][i+1] = pyr["filled"][i] - 2**i
      pyr["filled"][i] = 2**i

    # still too many ticks including the overflow?  cascade down.
    if pyr["filled"][i] + pyr["flowed"][i] > 2**i:
      pyr["flowed"][i+1] += ( pyr["filled"][i] + pyr[rope]["flowed"][i] ) - 2**i
      pyr["flowed"][i] = 2**i - pyr["filled"][i]

  # iterate again, calculating "empty"
  for i in range(0, 4):
    pyr["empty"][i] = 2**i - ( pyr["filled"][i] + pyr["flowed"][i] )






  # dataset to plot
  data={}


  data["title"] = "Pyramid for {} {}".format(abbrev[rope], grade.lower())
  data["date"] = "2018-xx-yy"


  # TODO: should be able to loop over these rather than generate each set manually
  data["row1"] = {}
  data["row1"]["title"] = validgrades[gradei].lower()
  data["row1"]["count"] = "({})".format(pyr["filled"][0])
  data["row1"]["squares"] = []
  for i in range(pyr["filled"][0]):
    data["row1"]["squares"].append("redpoint")
  for i in range(pyr["flowed"][0]):
    data["row1"]["squares"].append("cascade")
  for i in range(pyr["empty"][0]):
    data["row1"]["squares"].append("pending")

  data["row2"] = {}
  data["row2"]["title"] = validgrades[gradei - 1].lower()
  data["row2"]["count"] = "({})".format(pyr["filled"][1])
  data["row2"]["squares"] = []
  for i in range(pyr["filled"][1]):
    data["row2"]["squares"].append("redpoint")
  for i in range(pyr["flowed"][1]):
    data["row2"]["squares"].append("cascade")
  for i in range(pyr["empty"][1]):
    data["row2"]["squares"].append("pending")

  data["row3"] = {}
  data["row3"]["title"] = validgrades[gradei - 2].lower()
  data["row3"]["count"] = "({})".format(pyr["filled"][2])
  data["row3"]["squares"] = []
  for i in range(pyr["filled"][2]):
    data["row3"]["squares"].append("redpoint")
  for i in range(pyr["flowed"][2]):
    data["row3"]["squares"].append("cascade")
  for i in range(pyr["empty"][2]):
    data["row3"]["squares"].append("pending")

  data["row4"] = {}
  data["row4"]["title"] = validgrades[gradei - 3].lower()
  data["row4"]["count"] = "({})".format(pyr["filled"][3])
  data["row4"]["squares"] = []
  for i in range(pyr["filled"][3]):
    data["row4"]["squares"].append("redpoint")
  for i in range(pyr["flowed"][3]):
    data["row4"]["squares"].append("cascade")
  for i in range(pyr["empty"][3]):
    data["row4"]["squares"].append("pending")


  return jinja2.Environment(
    loader=jinja2.FileSystemLoader('./plot/')
  ).get_template('svg.j2').render(data)




# pyramid will print a page with links to graphs based on "file"
#

def pyramid(file = "ticks.csv", show = "RP"):

  # Call our function to turn the CSV file into ticks() data structure
  ticks = readticks(file, show)

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

  
  # CSV data is now loaded into structure, ready to generate links to our graphs
  outbuffer = ""

  
  
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
  
  
  # Pyramid is 4 rows high, so never start below 4th rung
  #
  
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
  

    # line wrap
    outbuffer += "\n<br/>\n"

    outbuffer += '<span style="white-space:nowrap">\n'
    for rope in usedrope:
      outbuffer += '<object type="image/svg+xml" data="/graph/{}/{}/{}/{}/" width="550" height="300" border="0"></object>\n'.format(file, show, rope, grade)

  
    outbuffer += '</span>'
    # TODO: need to analyse data anyway to determine if/when to end early

  
  
  return outbuffer

