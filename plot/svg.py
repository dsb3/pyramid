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

from plot.readcsv import readticks, count_pyr



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


  # TODO: If we try to graph for a grade "too low" (i.e. not four rows
  # before we hit the bottom), error out.


  # If we've requested a rope that wasn't used, error
  if rope not in ticks.keys():
     return "No data found"


  # Determine the date stamp for the pyramid.
  # - For each level gather the oldest ticks (redpoints, not cascades!)
  #   that are shown.  Of those ticks, find the newest.  So, the oldest
  #   tick in the top layer; the second oldest in second layer, fourth
  #   oldest in third, and eighth oldest in fourth.
  # - Of that set, find the newest.
  # - i.e. at what date did we stop accumulating new ticks?
  #   or, "when did we fill out the pyramid?"
  #

  alldates = []
  latestdate = ""
  for i in range(0, 4):
    # grade is gradei - i, number of boxes in row is 2^i
    # since ticks is sorted, gather the "last n" for the grade
    alldates += ticks[rope][ validgrades[gradei-i] ][-2**i:]

  if len(alldates):
    latestdate = sorted(alldates)[-1]
  else:
    latestdate = ""


  # TODO: enhance to capture flash/onsight/redpoint/etc.
  pyr=count_pyr(ticks, show, rope, grade)



  # dataset to plot
  data={}


  data["title"] = "Pyramid for {} {}".format(abbrev[rope], grade.lower())
  data["date"] = latestdate


  # TODO: should be able to loop over these rather than generate each set manually
  # count is total for that grade, not our truncated "graph this many" subset
  data["row1"] = {}
  data["row1"]["title"] = validgrades[gradei].lower()
  data["row1"]["count"] = "({})".format( len( ticks[rope][ (validgrades[gradei]) ] ))
  data["row1"]["squares"] = []
  for i in range(pyr["filled"][0]):
    data["row1"]["squares"].append("redpoint")
  for i in range(pyr["flowed"][0]):
    data["row1"]["squares"].append("cascade")
  for i in range(pyr["empty"][0]):
    data["row1"]["squares"].append("pending")

  data["row2"] = {}
  data["row2"]["title"] = validgrades[gradei - 1].lower()
  data["row2"]["count"] = "({})".format( len( ticks[rope][ (validgrades[gradei -1]) ] ))
  data["row2"]["squares"] = []
  for i in range(pyr["filled"][1]):
    data["row2"]["squares"].append("redpoint")
  for i in range(pyr["flowed"][1]):
    data["row2"]["squares"].append("cascade")
  for i in range(pyr["empty"][1]):
    data["row2"]["squares"].append("pending")

  data["row3"] = {}
  data["row3"]["title"] = validgrades[gradei - 2].lower()
  data["row3"]["count"] = "({})".format( len( ticks[rope][ (validgrades[gradei -2]) ] ))
  data["row3"]["squares"] = []
  for i in range(pyr["filled"][2]):
    data["row3"]["squares"].append("redpoint")
  for i in range(pyr["flowed"][2]):
    data["row3"]["squares"].append("cascade")
  for i in range(pyr["empty"][2]):
    data["row3"]["squares"].append("pending")

  data["row4"] = {}
  data["row4"]["title"] = validgrades[gradei - 3].lower()
  data["row4"]["count"] = "({})".format( len( ticks[rope][ (validgrades[gradei -3]) ] ))
  data["row4"]["squares"] = []
  for i in range(pyr["filled"][3]):
    data["row4"]["squares"].append("redpoint")
  for i in range(pyr["flowed"][3]):
    data["row4"]["squares"].append("cascade")
  for i in range(pyr["empty"][3]):
    data["row4"]["squares"].append("pending")


  # Shortcut for "don't print empty pyramids"
  # - if first and second rows are empty, don't print.
  # - we actually want to print empty pyramids between large gaps in ticks
  #   even if these should be rare in live data
  if pyr["empty"][0:2] == [1, 2]:
    data["nodata"] = 1


  return jinja2.Environment(
    loader=jinja2.FileSystemLoader('./plot/')
  ).get_template("svg.j2").render(data)



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
  outbuffer = "<html> <head> <title> Pyramids for {} </title> </head> <body>".format(file)

  
  
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
      outbuffer += '<object type="image/svg+xml" data="/svg/{}/{}/{}/{}/" width="550" height="300" border="0"></object>\n'.format(file, show, rope, grade)

  
    outbuffer += '</span>\n'
    # TODO: need to analyse data anyway to determine if/when to end early

  
  outbuffer += "</body></html>"
  
  return outbuffer


# highest will print a smaller page with only the highest pyramid included
#

def highest(file = "ticks.csv", show = "RP"):

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
  outbuffer = "<html> <head> <title> Highest pyramids for {} </title> </head> <body>".format(file)

  
  
  # Iterate top down through validgrades.  For each grade, if we have a tick
  # for either that grade, or the one below, we print it.
  
  # defaults to zero
  for rope in usedrope:
  
    # Pyramid is 4 rows high, so never start below 4th rung
    #
  
    for gradei in reversed(range( 3, len(validgrades))):
      grade=validgrades[gradei]
  
      # print this rope?
      if len( ticks[rope][validgrades[gradei-1]]) > 0 or len( ticks[rope][validgrades[gradei]]) > 0:
        outbuffer += "\n<br/>\n"
        outbuffer += '<object type="image/svg+xml" data="/svg/{}/{}/{}/{}/" width="550" height="300" border="0"></object>\n'.format(file, show, rope, grade)
        break


  return outbuffer

