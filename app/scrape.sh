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

# Doesn't work inside micro alpine container
# WGETOPT="-4"
WGETOPT=""


# GAE only.  If we're running in GAE, then chdir to /tmp which is writeable
if [ ! -z "$HTTP_X_APPENGINE_COUNTRY" -o ! -z "$GAE_APPLICATION" ]; then
  echo Running in GAE
  cd /tmp
fi


case "$1" in

  #
  # YOUR NAME HERE -- send a PR and I'll add the config
  #


  johndoe)
     DOC=1v1234512345123451234512345123451234512345xx
     wget $WGETOPT -O johndoe.csv $BASEURL$DOC${SUFFIX}0
     ;;


  # GAE hack - whenever we start a new instance we simply scrape
  # data before launching the flask app to render the first page
  #
  # Note: GAE puts all files in 
  start)
     DOC=1MU9vmWep4GDHleJo6Tw0BJb4fo0XjVJuz1p9uYgCrpg
     wget $WGETOPT -O dave.csv         $BASEURL$DOC${SUFFIX}0

     DOC=1sBWppVHHS_6b9kK68bdNMvCtLs0GHYjPxSgs5FT6_FI
     wget $WGETOPT -O joe.csv         $BASEURL$DOC${SUFFIX}0

     ;;


  # last / default
  dave|*)
     DOC=1MU9vmWep4GDHleJo6Tw0BJb4fo0XjVJuz1p9uYgCrpg

     wget $WGETOPT -O dave.csv         $BASEURL$DOC${SUFFIX}0
     wget $WGETOPT -O dave-boulder.csv $BASEURL$DOC${SUFFIX}1825018984
     wget $WGETOPT -O dave-rock.csv    $BASEURL$DOC${SUFFIX}447635240
     ;;

esac


