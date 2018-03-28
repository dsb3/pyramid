#!/bin/env python3
#
# Generate Horst training pyramids
#
# Config values used by other functions
#
# TO USE:
#   import cfg
#   print cfg.validyds
#
#

abbrev     = { "L":  "Lead", 
               "TR": "Top Rope",
               "DC": "Down Climb",
               "DL": "Down Lead",
               "Cx": "Climbing",  # Generic term for when rope isn't specified

               "B":  "Boulder",   # allow flexibility in separating bouldering gym/outdoors
               "IB": "Indoor Boulder",
               "OB": "Outdoor Boulder",

               "Trad":  "Trad",
               "Sport": "Sport",

               "OS": "Onsight",
               "F":  "Flash",
               "RP": "Redpoint",
               "RE": "Repeat",    # here and below aren't usually graphed
               "H":  "Hung",
               "A":  "Aided",
               "X":  "Failed Attempt",
             }


validrope   = ['TR', 'L', 'DC', 'DL', 'Cx', "B", "IB", "OB"]

# validascent can include "RE" (repeat) and better.  By default
# we only graph "RP" (first redpoint) and better.
validascent = ['RE', 'RP', 'F', 'OS']


# Yosemite Decimal System (shortened)
validyds = ["6", "7", "8", "9",
            "10a", "10b", "10c", "10d",
            "11a", "11b", "11c", "11d",
            "12a", "12b", "12c", "12d",
            "13a", "13b", "13c", "13d"
           ]

# Bouldering grades
validboulder = [ "v0", "v1", "v2", "v3",
                 "v4", "v5", "v6", "v7", "v8",
                 "v9", "v10", "v11", "v12" ]

# S.A., Oz.
validewbank = [ "10", "11", "12", "13", "14",
                "15", "16", "17", "18", "19",
                "20", "21", "22", "23", "24",
                "25", "26", "27", "28", "29" ]

# Font -- scales do not correlate for roped/boulders
validfont = [ "3", "4", "5", "6a", "6a+", "6b",
              "6b+", "6c", "6c+", "7a", "7a+",
              "7b", "7b+", "7c", "7c+", "8a" ]
 
# default to YDS
validgrades = validyds


