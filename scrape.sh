#!/bin/sh
#
# Hardcoded command to scrape from "public link" and
# refresh data
#

wget -O ticks.csv 'https://docs.google.com/spreadsheet/ccc?key=1MU9vmWep4GDHleJo6Tw0BJb4fo0XjVJuz1p9uYgCrpg&output=csv'

