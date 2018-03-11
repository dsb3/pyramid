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

  # Data structure to generate
  #
  # ticks {
  #   L {
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
  


  # If "show" is set, filter validascent so as to graph
  # only climbs of that type or better.
  # so: "RP" -> "RP", "F", "OS"
  # or: "OS" -> "OS" only
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
  

    # only include valid data items
    if rope not in validrope or ascent not in validascent or grade not in validgrades:
      continue
  
   
    # Append dates
    ticks[rope][grade].append(date)
  
    # TODO: append "attempt" dates to annotate graph
  
  
  
  # Parse through data before displaying (TODO: this is for future enhancements)
  for rope in ticks.keys():
    # Sort entries for each day
    for grade in ticks[rope].keys():
      ticks[rope][grade].sort(reverse=1)
  

  
  # Return the loaded data
  return ticks


# end readticks()

