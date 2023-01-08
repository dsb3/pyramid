#!/bin/env python3
#
# Generate Horst training pyramids
#
# Config values and functions used by other functions
#
# TO USE:
#   import cfg
#   print cfg.validyds
#
#

import os
import re
import sys
import yaml
import base64


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
               "Second": "Second",

               "OS": "Onsight",
               "F":  "Flash",
               "RP": "Redpoint",
               "RE": "Repeat",    # here and below aren't usually graphed
               "H":  "Hung",
               "A":  "Aided",
               "X":  "Failed Attempt",
             }


validrope   = ['TR', 'L', 'DC', 'DL', 'Cx', "B", "IB", "OB", "Trad", "Sport", "Second"]

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



# This is run one time when we launch.  It handles local config
# options - using the default ./config.yml, symlinking to use
# /data/config.yml instead, or writing a config fragment with
# a single data source instead
#
# I'm trying to make this both not-too-complicated, and also
# handle some of what I think will be expected use cases in
# case anyone who is not me wants to deploy the app.
#

def init_config():

  # If we have a Config Map in the expected place, symlink the
  # local config to use that instead (this also means changes in
  # the config map do not require a restart)
  if os.path.isfile("/data/config.yml"):
    # make sure this is a regular file, not a link
    if os.path.isfile("./config.yml") and not os.path.islink("./config.yml"):
      os.remove("./config.yml")
    print ("Debug: symlink /data/config.yml -> config.yml\n")
    try:
      os.symlink("/data/config.yml", "./config.yml")
    except:
      pass

  # For testing, also do this for an alternate path
  if os.path.isfile("./cmap-config.yml"):
    # make sure this is a regular file, not a link
    if os.path.isfile("./config.yml") and not os.path.islink("./config.yml"):
      os.remove("./config.yml")
    print ("Debug: symlink ./cmap-config.yml -> config.yml\n")
    try:
      os.symlink("./cmap-config.yml", "./config.yml")
    except:
      pass



  # Look at $CONFIG and write to config.yml if it's found
  confenv=os.environ.get('CONFIG', None)


  # #1 - do we have a simple URL?
  # https://docs.google.com/spreadsheets/d/xxPAGEIDxx/edit#gid=0
  # https://docs.google.com/spreadsheets/d/xxPAGEIDxx/export?format=csv&gid=0
  #

  if confenv:
    # Do we have a CONFIG url?
    # 
    url = re.compile(".*google.*/d/([^/]+)/.*gid=(\d+)")
    results = url.match(confenv) # , flags=re.IGNORECASE)
    if results:
      # if both args ...
      config={}
      config["default"] = "user"
      config["pages"] = {}
      config["pages"]["user"] = results.group(1)
      config["pages"]["todo"] = results.group(2)
      print ("Writing ./config.yml with $CONFIG data.\n", file=sys.stderr)
      fh = open("./config.yml", "w")
      fh.write( yaml.dump(config, default_flow_style=False) )
      fh.close()


    # Else, do we have a base64 string?
    b64 = ""
    try:
      b64 = base64.b64decode( confenv )
    except:
      pass

    if b64:
      # TODO - confirm syntax
      # "wb" needed to write bytes (versus string).
      fh = open("./config.yml", "wb")
      fh.write(b64)
      fh.close()






# Read config from fixed location
#
# TODO: now that we have user provided (not repo committed)
# config options, we need to sanity check our username for invalid
# chars and/or sanity check the contents of the config file read.

def read_config():
  # Read and return our config file as a dict
  config = yaml.load( open("./config.yml", "r") )

  # sanity check - we need a default user
  if "default" not in config.keys():
    config["default"] = "user"

  return config

