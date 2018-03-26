#!/bin/env python3
#
# Generate Horst training pyramids
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



# readticks will read a CSV file and populate ticks data structure

def readticks(file = "ticks.csv", show = "RP"):

  #
  # Data structure to generate
  #
  # ticks {
  #   'L' {
  #     11a [ date, date, ... ],
  #     10d [ date, date, ... ],
  #     ...
  #   }
  #   'TR' {
  #    ...
  #   }
  #
  # }
  

  # By default, we will show all ticks of "RP" (redpoint) or "better"
  # but if "show" is set, we filter validascent so as to graph only
  # climbs of that value or higher.
  #
  # So, default is: "RP", "F", "OS"
  # Passing "F" gives: "F", "OS" only
  # Passing "OS" gives: "OS" only
  # Passing an invalid value returns the whole suite: "RE", "RP", "F", "OS"
  #

  # NOTE: this edits the global variable validascent, also used
  # in the "display" functions.
  #
  try:
    if validascent.index(show.upper()) > 0:   # is NOT the first element
      del validascent[0: validascent.index(show.upper())]
  except ValueError:   # not in validascent at all, print everything
    pass



  # ticks data structure - this drives the graph output below
  ticks = {} 
  
  # Default header values to look for
  header_fields = { }
  first_row = 1

  # Default to avoid erroring
  validgrades = validyds     # already defaults to this value

  # Try to open file named as-is
  try:
    fh = open(file)
  except (FileNotFoundError, IOError):
    try:
      fh = open(file + ".csv")
    except (FileNotFoundError, IOError):
      return "File could not be opened"

  # Use a filter to strip comments from the CSV while we read it
  csvfile = csv.DictReader(filter(lambda row: row[0]!='#', fh))
  for row in csvfile:
  
    # Examine headers to try to auto-detect and adapt to variations.
    # TODO: this whole thing could be a lambda function
    #
    if first_row:
      for k in ["Date", "date"]:
        if k in row.keys():
          header_fields["date"] = k
          break

      for k in ["Grade", "grade", "YDS", "yds"]:
        if k in row.keys():
          header_fields["grade"] = k
          validgrades = validyds     # already defaults to this value
          break
      for k in ["V", "v"]:
        if k in row.keys():
          header_fields["grade"] = k
          validgrades = validboulder
          break
      for k in ["Ewbank", "ewbank"]:
        if k in row.keys():
          header_fields["grade"] = k
          validgrades = validewbank
          break
      for k in ["Font", "font"]:
        if k in row.keys():
          header_fields["grade"] = k
          validgrades = validfont
          break

      for k in ["Rope", "rope"]:
        if k in row.keys():
          header_fields["rope"] = k
          break

      for k in ["Ascent", "ascent", "Attempt", "attempt"]:
        if k in row.keys():
          header_fields["ascent"] = k
          break

      # Having examined header fields we don't re-examine on future rows
      first_row=0
  
      # Pre-populate our ticks data structure with data
      # to avoid constant checking for KeyError if we have
      # individual grades with no climbs logged
      for rope in validrope:
        ticks[rope] = {}
        for grade in validgrades:
          ticks[rope][grade] = []
  
  
  
    # These two are mandatory
    if "date" not in header_fields.keys() or "grade" not in header_fields.keys():
      return "CSV data headers are invalid"

    (date, grade) = (row[ header_fields["date"] ], row[ header_fields["grade"] ].lower())
  
    # We generate default values for these two
    try:
      rope = row[ header_fields["rope"] ]
    except KeyError:
      rope = "Cx"
  
    try:
      ascent = row[ header_fields["ascent"] ]
    except KeyError:
      ascent = "RP"
  
  
    # ensure valid date (also strips comments or extraneous lines)
    if not re.match("^20\d\d-\d\d-\d\d$", date):
      continue
  

    # Brief attempts to map entered grades into canonical grades if they
    # aren't already valid.
    # - drop and ignore any -/+ suffix
    # - drop and ignore any /x suffix (e.g. 11a/b -> 11a, or 25/26 -> 25)
    # - TODO: map naked 10 grade into 10b or 10c or ??
    # - TODO: handle capitalization errors
    # - TODO: handle optional 5. prefix for YDS
    if grade not in validgrades:
      grade = re.sub('[-+]*$',  '', grade)  # 8+    -> 8
      grade = re.sub('/[\w]+$', '', grade)  # 11a/b -> 11a
  

    # Is the row we read from the file valid?  If not, continue ...
    # only include valid data items
    if rope not in validrope or ascent not in validascent or grade not in validgrades:
      continue
  
    # If so, append it to our data structure
    ticks[rope][grade].append(date)


    # TODO: capture more data in the ticks structure
    # capture "attempt" dates to annotate; capture ascent type in structure
  
  
  # /end "for row in csvfile"


  # Before we return the data, we'll clean it up.

  for rope in ticks.keys():
 #   count = 0
    # Sort entries by date where they're found
    for grade in ticks[rope].keys():
      ticks[rope][grade].sort(reverse=1)
 #     count += len ( ticks[rope][grade] )

 #   # No ticks for this rope type?  Delete it.
 #   if count == 0:
 #     del ticks[rope]
  

  
  # Return the loaded data
  return ticks


# end readticks()



# count_pyr will read the ticks and create pyr structure for
# a single "show" (RP, F, OS, etc), single rope, and single grade
#
# TODO: count redpoint, flash, onsight separately
#
# dataset {
#   "filled" [ a, b, c, d ]            # count of climbed ticks at each row 
#   "flowed" [ a, b, c, d, overflow ]  # count of overflowed ticks
#   "empty"  [ a, b, c, d ]            # empty blocks to fill out pyramid
#



def count_pyr(ticks = "", show = "", rope = "", grade = ""):

  # grade should have been checked before calling this.
  gradei = validgrades.index(grade.lower())


  dataset = {}
  dataset["filled"]=[0, 0, 0, 0]      # empty four row pyramid for ticks
  dataset["flowed"]=[0, 0, 0, 0, 0]   # empty four row pyramid for surplus flowed from above, with unused fifth row var
  dataset["empty"]=[0, 0, 0, 0]       # empty four row pyramid for empty box count


  # Prefill "flowed" for the top row with a count of all climbs "above"
  for i in range(gradei+1, len(validgrades) - 1):
    dataset["flowed"][0] += len( ticks[rope][ (validgrades[i]) ] )

  # iterate over four rows, capturing "filled" from our ticks data
  for i in range(0, 4):
    dataset["filled"][i] = len( ticks[rope][ (validgrades[gradei - i]) ] )

  # iterate again, cascading excess count into "flowed"
  for i in range(0, 4):
    # too many ticks for this row?  overflow to the next row.
    if dataset["filled"][i] > 2**i:
      dataset["flowed"][i+1] = dataset["filled"][i] - 2**i
      dataset["filled"][i] = 2**i

    # still too many ticks including the overflow?  cascade down.
    if dataset["filled"][i] + dataset["flowed"][i] > 2**i:
      dataset["flowed"][i+1] += ( dataset["filled"][i] + dataset["flowed"][i] ) - 2**i
      dataset["flowed"][i] = 2**i - dataset["filled"][i]

  # iterate again, calculating "empty"
  for i in range(0, 4):
    dataset["empty"][i] = 2**i - ( dataset["filled"][i] + dataset["flowed"][i] )


  return dataset
