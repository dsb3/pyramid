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
from dateutil import parser
from dateutil.relativedelta import *

# Import our cfg variables (definitions of rope types, grades, etc)
from plot.cfg import abbrev, validrope, validascent, \
        validyds, validboulder, validewbank, validsport, validgrades



# readticks will read a CSV file and populate ticks data structure

def readticks(file = "ticks.csv", show:str = "RP"):

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

  # Take a copy of validascent (global) before deleting elements
  plotascent = validascent[:]

  try:
    if plotascent.index(show.upper()) > 0:   # is NOT the first element
      del plotascent[0: plotascent.index(show.upper())]
  except ValueError:   # not in plotascent at all, print everything
    pass



  # ticks data structure - this drives the graph output below
  ticks = {} 
  
  # Default header values to look for
  header_fields = { }
  first_row = 1

  # Default to avoid erroring
  validgrades = validsport     # already defaults to this value


  # Try to open file from /tmp first (GAE hack)
  try:
    fh = open("/tmp/" + file + ".csv")
  except (FileNotFoundError, IOError):
    try:
      fh = open(file + ".csv")
    except (FileNotFoundError, IOError):
        return { "Failed:": "File could not be opened" }

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

      for k in ["Grade", "grade", "Font", "font"]:
        if k in row.keys():
          header_fields["grade"] = k
          validgrades = validsport
          break

      for k in ["YDS", "yds"]:
        if k in row.keys():
          header_fields["grade"] = k
          validgrades = validyds     # This was previously the default; now defaults to font
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
    # - handle optional 5. prefix for YDS
    # - drop and ignore any -/+ suffix
    # - drop and ignore any /x suffix (e.g. 11a/b -> 11a, or 25/26 -> 25)
    # - TODO: map naked 10 grade into 10b or 10c or ??
    # - TODO: handle capitalization errors
    if grade not in validgrades:
      grade = re.sub('^5\.(\d)', '\g<1>', grade)  # 5.8   -> 8
      grade = re.sub('[-+]*$',  '', grade)        # 8+    -> 8
      grade = re.sub('/[\w]+$', '', grade)        # 11a/b -> 11a
      grade = re.sub('^([345])[abc]', '\g<1>', grade) # 4a, 4b, 4c -> 4; 5a, 5b, 5c -> 5


    # Is the row we read from the file valid?  If not, continue ...
    # only include valid data items
    if rope not in validrope or ascent not in plotascent or grade not in validgrades:
      continue
  
    # If so, append it to our data structure
    ticks[rope][grade].append(date)


    # TODO: capture more data in the ticks structure
    # capture "attempt" dates to annotate; capture ascent type in structure
  
  
  # /end "for row in csvfile"
  fh.close()


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
  



  ## TODO: refactor this.
  #  get all dates; then strip for only last N months (currently hardcoded)

  # Extract all dates for valid data, which we can then min() and max() on
  all_dates = set([ ])
  for r in ticks.keys():
    for g in ticks[r].keys():
      all_dates |= set( ticks[r][g] )

  # NEW -- look at "max date - 3 months" to start to filter for a rolling
  #
  # - this needs some careful thought.  If we have too short of a rolling window
  #   then the various gym routes which were climbed when first put up might "roll off"
  #   and disappear since subsequent RE climbs won't be shown.
  #
  # - TODO: only enable rolling for gym climbs, perhaps in the config.yml file?
  #         option for different lengths of rolling, perhaps in web ui?
  #
  # get the latest date in the list, parse it, subtract 3 months,
  # turn back into isoformat, and truncate to return YYYY-MM-DD
  cutoff = ( parser.parse(max(all_dates)) - relativedelta(months=3) ).isoformat()[0:10]

  # Now iterate through ticks again and delete anything older.
  # loop through ropes
  for r in ticks.keys():
    # loop through grades
    for g in ticks[r].keys():
      trimmedset = list(x for x in ticks[r][g] if x > cutoff)
      ticks[r][g] = trimmedset

  ## month limit


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
