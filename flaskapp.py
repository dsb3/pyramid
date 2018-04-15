#!/bin/env python

import os
from flask import Flask, Response, redirect, request, send_from_directory
from werkzeug.routing import BaseConverter

# text graph creator
from plot.text import pyramid as text_pyramid

# graphical creator
from plot.svg import pyramid as graph_pyramid
from plot.svg import highest as graph_highest
from plot.svg import one_svg

# scrape new data
from plot.scrape import scrape

# initialize to use 
from plot.cfg import init_config, read_config


# Create application with /static path defined
application = Flask(__name__, static_url_path='/static')

# cut/pasted from stack exchange to permit regex in routes
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

application.url_map.converters['regex'] = RegexConverter



# Special cases for index, favicon and robots, which feed from /static/ even
# though the URL does not contain that path
@application.route("/")
def hello():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               "index.html", mimetype='text/html')

@application.route('/favicon.ico')
def favicon():
    # Send a different favicon to distinguish when running on "L"ocalhost
    if "localhost" in request.host or "127.0.0.1" in request.host or "0.0.0.0" in request.host:
      ico = "favicon.L.ico"
    else:
      ico = "favicon.ico"
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               ico, mimetype='image/vnd.microsoft.icon')

@application.route('/robots.txt')
def robotstxt():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               "robots.txt", mimetype='text/plain')

@application.route('/health')
def health():
    # TODO - print other health information.  uptime, # of pages served,
    # number of threads, etc.
    return "OK"

#########


@application.route('/text/')
@application.route('/graph/')
@application.route('/highest/')
@application.route('/scrape/')
def default_user():
    config = read_config()
    return redirect(request.base_url + config["default"], code=302)

 
#########


@application.route('/text/<regex("[A-Za-z0-9-]+(.csv)?"):plotfor>/')
def text_user(plotfor):
    return text_pyramid(file = plotfor, show="RP")


@application.route('/text/<regex("[A-Za-z0-9-]+(.csv)?"):plotfor>/<regex("[A-Za-z]+"):showfor>/')
def text_user_ascent(plotfor, showfor):
    return text_pyramid(file = plotfor, show=showfor.upper())


#########


# /graph/dave/  <-- page of all graphs
@application.route('/graph/<regex("[A-Za-z0-9-]+(.csv)?"):plotfor>/')
def graph_user(plotfor):
    return graph_pyramid(file = plotfor, show="RP")

# /graph/dave/OS/  <-- page of all graphs
@application.route('/graph/<regex("[A-Za-z0-9-]+(.csv)?"):plotfor>/<regex("[A-Za-z]+"):showfor>/')
def graph_user_ascent(plotfor, showfor):
    return graph_pyramid(file = plotfor, show=showfor.upper())



# /highest/dave/  <-- page of highest pyramid only for each rope
@application.route('/highest/<regex("[A-Za-z0-9-]+(.csv)?"):plotfor>/')
def highest_user(plotfor):
    return graph_highest(file = plotfor, show="RP")

# /highest/dave/OS/  <-- page of highest pyramids with ascent qualifier
@application.route('/highest/<regex("[A-Za-z0-9-]+(.csv)?"):plotfor>/<regex("[A-Za-z]+"):showfor>/')
def highest_user_ascent(plotfor, showfor):
    return graph_highest(file = plotfor, show=showfor.upper())



# /svg/dave/OS/TR/10b/  <-- one svg
# Need to override default text/html mimetype for proper rendering
@application.route('/svg/<regex("[A-Za-z0-9-]+(.csv)?"):plotfor>/<regex("[A-Za-z]+"):showfor>/<regex("[A-Za-z]+"):showrope>/<regex("[A-Za-z0-9.]+"):showgrade>/')
def svg_user_ascent_rope_grade(plotfor, showfor, showrope, showgrade):
    content = one_svg(file = plotfor, show=showfor.upper(), rope=showrope.upper(), grade=showgrade.upper())
    return Response(content, mimetype="image/svg+xml")


#########


@application.route('/scrape/<regex("[A-Za-z0-9-]+"):plotfor>/')
def scrape_user(plotfor):
    return scrape(user = plotfor)


#########


# Note, this is literally "before first request", i.e. at the
# time the first request is received, and not when the app starts.
@application.before_first_request
def get_ready_get_set():
  init_config()




if __name__ == "__main__":
  application.run(debug=True)



