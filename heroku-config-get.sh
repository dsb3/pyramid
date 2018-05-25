#!/bin/sh
#
# Simple script to turn the current config.yml into a base64 config variable
#
# Cut/paste the output back into the command line, or into the web ui
#

echo "# Current CONFIG contents:"
CONFIG=$( heroku config:get CONFIG )

if [ -z "$CONFIG" ]; then
  echo "(empty)"
else
  echo "$CONFIG"
  echo
  echo "# Decoded:"
  echo "$CONFIG" | base64 -d
fi

