#!/bin/env python

import os
from flask import Flask, Response, send_from_directory
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

@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@application.route('/plot/<regex("[A-Za-z]+(.csv)?"):plotfor>/')
def example1(plotfor):
    #ctype = "text/plain"
    #data = text_pyramid(file = plotfor, show="RP")
    #return Response(data, mimetype=ctype)
    return "<pre>" + text_pyramid(file = plotfor, show="RP")



@application.route('/plot/<regex("[A-Za-z]+(.csv)?"):plotfor>/<showfor>/')
def example2(plotfor, showfor):
    ctype = "text/plain"
    data = text_pyramid(file = plotfor, show=showfor)
    return Response(data, mimetype=ctype)


if __name__ == "__main__":
    application.run(debug=True)

