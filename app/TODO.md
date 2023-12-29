# TODO

## environment

Make sure pipenv runs properly, with correct libraries

Make notes on sequence to update, if needed.

Manage directory to store persisted files better (e.g. GAE cannot write to root filesystem).  Option to dump in /tmp.  This is preferred for kubernetes deployment as well to allow us to set readOnlyRootFilesystem.

Manage other ways of storing persisted files.  Again, GAE is the use case using google data storage calls, not local file system i/o to behave properly in that environment.


## health check

/healthz check or similar, which can also populate first scrape content


## flask vs django

We need an admin page to edit/update scrape sources to
avoid hard coding the google doc sources.  Maybe django
is a better framework for more complex operations?



## gid=

Support gid for downloading different sheets in one doc

Support gid for combining multiple sheets in the same doc (e.g. when the sheet
gets too long, split into "ticks 201x-Q1", "ticks-201x-Q2", etc...)

Support google IAM credentials to download protected pages


## data

- read csv one time and process; then store serialized data object for faster processing


## html

- home page

- links to other pages, scraper etc



## text

- revert to "print the whole column" for text output


## dates

- support "show last X months" data filter


## svg

- headers for each vertical column (don't repeat inside each block)

- implement "don't start until" and "stop plotting when" to only show pertinent graphs for each rope

- shrink image to fit 3x wide more easily

- show RP / F / OS

- slider to adjust RP / F / OS

- hyperlink in /highest/ output for deeper data

- different colours for different ropes

- fade boxes to indicate old dates

- show the colours of the routes that were climbed; hover/mouseover to show detail

- show/hide legend based on what's being graphed

- animate playing forward through time to show pyramids filling in

- add date stamp to "last change for this pyramid"






