#!/bin/env python

import os
from flask import Flask, Response, redirect, request, send_from_directory
from werkzeug.routing import BaseConverter

# text graph creator
from plot.text import pyramid as text_pyramid


# scrape new data
from plot.scrape import scrape


# Create application with /static path defined
application = Flask(__name__, static_url_path='/static')

# cut/pastd from stack exchange to permit regex in routes
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

#########

@application.route('/text/<regex("[A-Za-z0-9-]+(.csv)?"):plotfor>/')
def example1(plotfor):
    #ctype = "text/plain"
    #data = text_pyramid(file = plotfor, show="RP")
    #return Response(data, mimetype=ctype)
    return "<pre>" + text_pyramid(file = plotfor, show="RP")



@application.route('/text/<regex("[A-Za-z0-9-]+(.csv)?"):plotfor>/<showfor>/')
def example2(plotfor, showfor):
    ctype = "text/plain"
    data = text_pyramid(file = plotfor, show=showfor)
    return Response(data, mimetype=ctype)


if __name__ == "__main__":
    application.run(debug=True)



#########

@application.route('/scrape/<regex("[A-Za-z0-9-]+"):plotfor>/')
def example3(plotfor):
    return "<pre>" + scrape(user = plotfor)



