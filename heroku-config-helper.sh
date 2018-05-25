#!/bin/sh
#
# Simple script to turn the current config.yml into a base64 config variable
#
# Cut/paste the output back into the command line, or into the web ui
#

echo "# Current config.yml contents:"
cat config.yml | sed -e 's/^/# /'

echo 
echo "# Cut/paste this command to set this as your heroku local config"
echo heroku config:set CONFIG=$( base64 config.yml -w 0 )

