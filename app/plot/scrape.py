#!/bin/env python3
#
# Scrape google sheets data as CSV
#
# TODO:
# - capture sheet gid= to allow downloading different data
# - avoid downloading one file too often (rate limit)
# - handle/trap errors on URL downloading
# - limit to ipv4 only (ipv6 can cause delays in downloading)
# - handle google auth service accounts
#

import sys
import re
import urllib.request

from plot.cfg import read_config


# Scrape (download) data for the named user.
#
# sub is either a gid (numeric sheet identifier) or
# a word to look up in our dictionary
#

def scrape(user = "dave", sub = "0"):

  config = read_config()

  if user not in config["pages"].keys():
    return "<pre>User not defined"

  # format is PAGEID with optional /GID
  m = re.search(r'^([A-Za-z0-9-]+)/?(\d+)?$', config["pages"][user])

  if m:
    page = m.group(1) or ""
    gid = m.group(2) or "0"
  else:
    return "<pre>User not configured correctly"


  # Generate URL to access, read data and convert to a string
  url="https://docs.google.com/spreadsheets/d/" + page + "/export?format=csv&gid=" + gid

  ## DEBUG: uncomment this to just show what URL is configured
  ## return "<pre>" + url

  data = urllib.request.urlopen(url).read().decode("utf-8")


  # Sanity check content

  # If this text exists, the google doc spreadsheet isn't readable by all
  if data.find('<html lang="') != -1:
    return "<pre>Content not readable. Check that public sharing is enabled."

 
  # debug
  import os
  dir_path = os.path.dirname(os.path.realpath(__file__))
  cwd = os.getcwd()
  print (cwd)

  # Save to disk
  # GAE hack - if we can't write in cwd, divert to /tmp
  try:
      fh = open("./" + user + ".csv", "w")
      fh.write(data)
      fh.close()
  except OSError as e:
      fh = open("/tmp/" + user + ".csv", "w")
      fh.write(data)
      fh.close()

  
  # Extract last line to return as a status indicator
  lines = data.split("\r\n")
  return "<pre>Last line: " + lines[-1]


