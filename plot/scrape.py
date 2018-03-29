#!/bin/env python3
#
# Scrape google sheets data as CSV
#
# TODO:
# - capture sheet gid= to allow downloading different data
# - avoid downloading one file too often (rate limit)
# - handle/trap errors on URL downloading
# - limit to ipv4 only (ipv6 can cause delays in downloading)
#


import sys
import re
import urllib.request


# Hard-coded page ID prevents user from requesting random URLs
pages = {
  "dave":  "1MU9vmWep4GDHleJo6Tw0BJb4fo0XjVJuz1p9uYgCrpg",
  "shane": "1v30fRnnKASoTLeEuGRo0Zg2hcwOSqE95N9B74v4UhAs",
  "cole":  "15cOnJtF9VmatGTyBjB5W5qz3rJ_yuUgmfLEYDJvOHjg",
  "mary":  "16qmOaUZFPqneBN9bAbyn8fuDlcAvsJ0GdwKRec7rmWo"
}


# Scrape (download) data for the named user.
#
# sub is either a gid (numeric sheet identifier) or
# a word to look up in our dictionary
#

def scrape(user = "dave", sub = "0"):

  if user not in pages.keys():
    return "<pre>User not defined"

  # hard coded - first page.
  gid="0"


  # Generate URL to access, read data and convert to a string
  url="https://docs.google.com/spreadsheets/d/" + pages[user] + "/export?format=csv&gid=" + gid
  data = urllib.request.urlopen(url).read().decode("utf-8")


  # Sanity check content

  # If this text exists, the google doc spreadsheet isn't readable by all
  if data.find('<html lang="') != -1:
    return "<pre>Content not readable. Check that public sharing is enabled."

  
  # Save to disk
  fh = open(user + ".csv", "w")
  fh.write(data)
  fh.close()
  
  # Extract last line to return as a status indicator
  lines = data.split("\r\n")
  return "<pre>Last line: " + lines[-1]


