#!/bin/sh
#
# Hardcoded command to scrape from "public link" and
# refresh data
#
# NOTES:
# - wget -4 skips ipv6 delay/timeouts
# - Alternate method is to use this URL format:
#     wget -4 -O dave.csv 'https://docs.google.com/spreadsheet/ccc?key=1MU9vmWep4GDHleJo6Tw0BJb4fo0XjVJuz1p9uYgCrpg&output=csv'
#

# Take the regular URL to edit:
# https://docs.google.com/spreadsheets/d/1MU9vmWep4GDHleJo6Tw0BJb4fo0XjVJuz1p9uYgCrpg/edit#gid=0
#
# Replace /edit#gid=num with /export?format=XXX&gid=num
#

BASEURL="https://docs.google.com/spreadsheets/d/"
SUFFIX="/export?format=csv&gid="

case "$1" in

  #
  # YOUR NAME HERE -- send a PR and I'll add the config
  #


  johndoe)
     DOC=1v1234512345123451234512345123451234512345xx
     wget -4 -O shane.csv $BASEURL$DOC${SUFFIX}0
     ;;


  # last / default
  dave|*)
     DOC=1MU9vmWep4GDHleJo6Tw0BJb4fo0XjVJuz1p9uYgCrpg

     wget -4 -O dave.csv         $BASEURL$DOC${SUFFIX}0
     wget -4 -O dave-boulder.csv $BASEURL$DOC${SUFFIX}1825018984
     wget -4 -O dave-rock.csv    $BASEURL$DOC${SUFFIX}447635240
     ;;

esac


