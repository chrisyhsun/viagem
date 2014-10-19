#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import logging
import os
import jinja2
from google.appengine.ext import ndb
import urllib2
import json
import random
from models import Reference, Result, AUTH_KEYS, themes

current_key = 0
AUTH_KEY = AUTH_KEYS[0]

jinja_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('home.html')
        self.response.out.write(template.render(template_values))


class SearchHandler(webapp2.RequestHandler):
    def get(self):
        place = self.request.get('place')
        theme = self.request.get('theme')
        if theme == 'random':
            theme = random.choice(themes.keys())

        tempaddress = place.replace(' ', '+')

        coordinates_json = getCoordinates(place)
        
        if not place:
            template_values = {'response' : 'You must enter a location to search.'}
            template = jinja_environment.get_template('home.html')
            self.response.out.write(template.render(template_values))
        elif coordinates_json['status'] == 'ZERO_RESULTS':
            template_values = {'response' : 'Your search returned no results.'}
            template = jinja_environment.get_template('home.html')
            self.response.out.write(template.render(template_values))
        elif coordinates_json['status'] == 'OVER_QUERY_LIMIT':
        	current_key += 1
        	AUTH_KEY = AUTH_KEYS[current_key]
        else:
            # turn place into latlng \/
            lat = coordinates_json['results'][0]['geometry']['location']['lat']
            lon = coordinates_json['results'][0]['geometry']['location']['lng']
            location =  str(lat) + ',' + str(lon)
            # radius in meters \/
            radius = 10000
            # search all api text info for these keywords \/
            keywords = makeKeywords(theme)

            references = getReferences(location, radius, keywords)
            searchreferences = makeReferenceObjects(references)
            urldict = makeUrls(searchreferences)
            template_values = {'urldict':urldict, 'previous_place':place}
            template = jinja_environment.get_template('searchresults.html')
            self.response.out.write(template.render(template_values))

# helper functions 

def makeKeywords(theme):
    '''
    takes a theme, and makes a string of the form word+word+word
    from the model
    '''
    keywords = ''
    for word in themes[theme]:
        keywords += word + '+'
    return keywords[:-1]

def getCoordinates(address):
    '''
    takes a string location and returns the json data needed to get the lat/lon
    requires further parsing
    '''
    address = urllib2.quote(address)
    geocode_url="http://maps.googleapis.com/maps/api/geocode/json?address=%s" % address
    response = urllib2.urlopen(geocode_url)
    json_raw = response.read()
    jsonresponse = json.loads(json_raw)
    #logging.info(jsonresponse)
    return jsonresponse

def getReferences(location, radius, keywords):
    '''
    given a location, radius, and keywords,
    returns json data with all the reference objects of the results
    requires further parsing
    '''
    url = ('https://maps.googleapis.com/maps/api/place/search/json?location=%s'
         '&radius=%s&key=%s&keyword=%s') % (location, radius, AUTH_KEY, keywords)
    response = urllib2.urlopen(url)
    json_raw = response.read()
    json_data = json.loads(json_raw)
    #logging.info('in getReferences')
    #logging.info(json_data)
    return json_data

def makeReferenceObjects(references):
    tempreferences = []
    if references['status'] == 'OK':
        for place in references['results']:
            # create Reference object with fields 'name' and 'reference' for clarity
            reference = Reference(name = place['name'], reference = place['reference'])
            #logging.info(reference)
            tempreferences.append(reference)
        return tempreferences

# go through list of references, create http request for each,
def makeUrls(references):
    urls = {}
    if references:
        for reference in references:
            url = 'https://maps.googleapis.com/maps/api/place/details/json?key=' + AUTH_KEY + '~reference=' + reference.reference
            urls[reference.name] = url
        return urls
    else:
        return 'no results'    


def getPlusUrl(data):
    if 'result' in data and 'url' in data['result']:
        url = data['result']['url']
    else:
        url = 'No google plus page available'
    return url

def getAddress(data):
    if 'result' in data and 'formatted_address' in data['result']:
        address = data['result']['formatted_address']
    else:
        address = 'no address available'
    return address

# check if a phone number is listed
def getPhone(data):
    if 'result' in data and 'formatted_phone_number' in data['result']:
        phone = data['result']['formatted_phone_number']
    else:
        phone = 'no phone number available'
    return phone

# check if a website is listed
def getSite(data):
    if 'result' in data and 'website' in data['result']:
        site = data['result']['website']
    else:
        site = 'No website available'
    return site

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/search', SearchHandler)
], debug=True)
