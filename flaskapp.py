#!/bin/env python

from flask import Flask, Response
from werkzeug.routing import BaseConverter

# text graph creator
from plot.text import pyramid as text_pyramid


application = Flask(__name__)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

application.url_map.converters['regex'] = RegexConverter


@application.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"



@application.route('/plot/<regex("[A-Za-z]+(.csv)?"):plotfor>/')
def example1(plotfor):
    ctype = "text/plain"
    data = text_pyramid(file = plotfor, show="RP")

    return Response(data, mimetype=ctype)


@application.route('/plot/<regex("[A-Za-z]+(.csv)?"):infile>/<show>/')
def example2(infile, show):
    return "infile: %s, show: %s" % (infile, show)


if __name__ == "__main__":
    application.run(debug=True)

