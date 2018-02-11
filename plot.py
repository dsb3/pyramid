#!/bin/env python2
#
# Plot Horst training pyramids for "ticks.csv" in current directory
#

import re
import csv

from datetime import datetime


# Data structure to generate
#
# ticks {
#   L {
#     newest = date    # used for age gradients
#     11a { 
#       OS [ date, date, ... ]
#       F  [ date, date, ... ]
#       RP [ date, date, ... ]
#     }
#     10d { ... }
#     ...
#   }
#   TR {
#    ...
#   }
# }

# Load data file
# Date, Grade, Rope, Ascent, (ignored)
#

# Ignore any ascents that don't get graphed
# - OS, F, RP
#
# TODO: later include RE for mileage graphs.
#

abbrev     = { "L":  "Lead", 
               "TR": "Top Rope",
               "OS": "Onsight",
               "F":  "Flash",
               "RP": "Redpoint",
               "RE": "Repeat",    # here and below aren't graphed yet
               "H":  "Hung",
               "A":  "Aided",
               "X":  "Failed Attempt",
             }


validrope   = ['TR', 'L']
validascent = ['OS', 'F', 'RP']

validgrades = ["6", "7", "8", "9",
               "10a", "10b", "10c", "10d",
               "11a", "11b", "11c", "11d",
               "12a", "12b", "12c", "12d",
               "13a", "13b", "13c", "13d"
              ]


ticks = {} 
newest = {}
highest = {}


# Pre-populate our ticks data structure with data
# to avoid constant checking for KeyError if we have
# individual grades with no climbs logged
for rope in validrope:
  ticks[rope] = {}
  newest[rope] = "2000-00-00"
  for grade in validgrades:
    ticks[rope][grade] = []


with open('ticks.csv', 'rb') as csvfile:
  csvfile = csv.reader(csvfile)
  for row in csvfile:
    # Need at least four elements
    if len(row) < 4:
      continue

    # extract data
    (date, grade, rope, ascent) = row[:4]

    # ensure valid date (also strips header lines)
    if not re.match("^20\d\d-\d\d-\d\d$", date):
      continue

    # Brief attempts to map entered grades into canonical grades.
    # - drop and ignore any -/+ suffix
    # - drop and ignore any /x suffix (e.g. 11a/b -> 11a)
    # - TODO: map naked 10 grade into 10b or 10c or ??
    grade = re.sub('[-+]$', '', grade)   # 8+    -> 8
    grade = re.sub('(1[0-5][abcd])/[abcd]$', '\\1', grade)    # 11a/b -> 11a


    # only include valid data items
    if rope not in validrope or ascent not in validascent or grade not in validgrades:
      continue

    # Save newest tick seen for rope type for aging ticks
    if newest[rope] < date:
      newest[rope] = date
 
    # Append dates
    ticks[rope][grade].append(date)

    # TODO: append "attempt" dates to annotate graph



# Parse through data before displaying (TODO:  this is for future enhancements)
for rope in ticks.keys():
  # Sort entries for each day
  for grade in ticks[rope].keys():
    ticks[rope][grade].sort(reverse=1)

  # Save max grade for each rope type
  # - take the keys (grades) for this rope, and sort them by comparing the
  #   relative index inside validgrades, then save the last element
  highest[rope] = sorted( ticks[rope].keys(), cmp=lambda x,y:cmp(validgrades.index(x), validgrades.index(y)))[-1]


# CSV data is now loaded into struct.





# TODO: look at SVG output to be interactive

# Output format
#
# LEAD              ---- TOPROPE           ---- ...
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
# Each vertical strip is generated separately.  I want these to line
# up horizontall, -- the separation between them being an indication of
# lead to tr discrepancy.

# Overfull grades flow down to empty holes below

# SVG dynamic slider -- slide RE/ RP/ F/ OS



# First draft -- Print text output
# (deal with graphics later)


# Data structure to generate separately for each grade we graph
#
# pyr {
#   "TR" {
#     "filled" [ a, b, c, d ]            # count of climbed ticks at each row - graphed as [X]
#     "flowed" [ a, b, c, d, overflow ]  # count of overflowed ticks - graphed as [+]
#     "empty"  [ a, b, c, d ]            # empty blocks to fill out pyramid - graphed as [ ]
#     }
#   "L" { ... }
#

# Iterate top down through validgrades.  For each grade, if we have a tick
# for either that grade, or the one below, we start printing pyramids.  If
# we don't have a tick for either TR/L then we print a blank space, not an
# empty pyramid
# 


# Pyramid is 4 rows high, so can't start below 4th rung
#
# We need grade as an index into validgrades more often than we need "grade",
# the textual equivalent

print_for={}

for gradei in reversed(range( 3, len(validgrades))):
  grade=validgrades[gradei]

  # for this row, do I print anything?
  print_row=0

  # if I need to print for either rope, we output on both
  for rope in validrope:
    if len( ticks[rope][validgrades[gradei-1]]) > 0 or len( ticks[rope][validgrades[gradei]]) > 0:
      print_row = 1
      print_for[rope] = 1
    else:
      print_for[rope] = 0

  # nothing yet?  continue on next grade
  if not print_row:
    continue

  # TODO:
  # Handle unusual case of missing rows in the middle of the data set.



  # gather row data for validropes.
  pyr={}
  for rope in validrope:
    pyr[rope]={}
    pyr[rope]["filled"]=[0, 0, 0, 0]      # empty four row pyramid for ticks
    pyr[rope]["flowed"]=[0, 0, 0, 0, 0]   # empty four row pyramid for surplus flowed from above, with unused fifth row var
    pyr[rope]["empty"]=[0, 0, 0, 0]       # empty four row pyramid for empty box count


    # Prefill "flowed" for the top row with a count of all climbs "above"
    for i in range(gradei+1, len(validgrades) - 1):
      pyr[rope]["flowed"][0] += len( ticks[rope][ (validgrades[i]) ] )


    # iterate over four rows, capturing "filled" from our ticks data
    for i in range(0, 4):
      pyr[rope]["filled"][i] = len( ticks[rope][ (validgrades[gradei - i]) ] )

    # iterate again, cascading excess count into "flowed"
    for i in range(0, 4):
      # too many ticks for this row?  overflow to the next row.
      if pyr[rope]["filled"][i] > 2**i:
        pyr[rope]["flowed"][i+1] = pyr[rope]["filled"][i] - 2**i
        pyr[rope]["filled"][i] = 2**i

      # still too many ticks including the overflow?  cascade down.
      if pyr[rope]["filled"][i] + pyr[rope]["flowed"][i] > 2**i:
        pyr[rope]["flowed"][i+1] += ( pyr[rope]["filled"][i] + pyr[rope]["flowed"][i] ) - 2**i
        pyr[rope]["flowed"][i] = 2**i - pyr[rope]["filled"][i]

    # iterate again, calculating "empty"
    for i in range(0, 4):
      pyr[rope]["empty"][i] = 2**i - ( pyr[rope]["filled"][i] + pyr[rope]["flowed"][i] )



  # TODO:
  # - if pyramid is full of ticks, stop printing this rope type after one full card
  # - if pyramid is full of ticks/overflow, stop printing after TWO full cards
  # If either match, then below either print blank spot (blank one rope type) or
  # stop processing (blank all rope types)


  # Header, if we have data in the top two rows
  print
  for rope in validrope:
    if pyr[rope]["filled"][:2] == [0, 0]:
      header=""
      print "         {:^32}".format(header),
    else:
      header="Pyramid for %s %s" % ( abbrev[rope], grade)
      print " gr( ##) {:^32} ".format(header),
  print

  # print pyramid, row by row
  for i in range(0, 4):
    # row length is 1, 2, 4, 8 (or 2**j)
    for rope in validrope:
      filled=pyr[rope]["filled"][i]
      flowed=pyr[rope]["flowed"][i]
      empty=pyr[rope]["empty"][i]
      # empty=0

      # we might not be printing 
      if pyr[rope]["filled"][:2] == [0, 0]:
        boxes=""
      else:
        boxes="[X] "*filled + "[+] "*flowed + "[ ] "*empty

      # Squelch row prefix if not printing
      if pyr[rope]["filled"][:2] == [0, 0]:
        row_prefix=""
      else:
        row_prefix="{:>3}({:3})".format( validgrades[gradei-i], len( ticks[rope][ validgrades[gradei-i] ] ) )
      
      print "{:6} {:^32} ".format( row_prefix, boxes ), 
    print ""


