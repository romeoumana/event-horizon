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
import jinja2
import os
import logging
import json
import httplib2
import urllib
import simplejson
import eventful

from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb

class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    number = ndb.StringProperty(required=True) # change to int property later

class Profile(ndb.Model):
    name = ndb.StringProperty(required=True)

class Event(ndb.Model):
    name = ndb.StringProperty(required=True)
    location = ndb.GeoPtProperty(required=True)
    time = ndb.DateTimeProperty(required=True)
    description = ndb.TextProperty(required=True)
    pictures = ndb.BlobProperty(required=True)

class RomeoHandler(webapp2.RequestHandler):
    def get(self):
        template= jinja_environment.get_template('templates/romeo.html')
        self.response.write(template.render({'results': "no swag"}))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template= jinja_environment.get_template('templates/home.html')
        self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
    def post(self):
        #!/usr/bin/env python

        api = eventful.API('test_key', cache='.cache')
        events = api.call('/events/search', q='music', l='San Diego')

        for event in events['events']['event']:
            self.response.write("%s at %s" % (event['title'], event['venue_name']))


        '''
        results_template= jinja_environment.get_template('templates/results.html')
        base_url = "http://eventful.com/json/events?"
        search_type = 'q='
    #    api_key_url = "&api_key=P39qwcnBXLTHTnP3"
        search_term=self.request.get('query')
        search_term= search_term.replace(' ', '+')
        url=base_url + search_type + search_term #+ api_key_url
        logging.info(url)
        eventful_data_source= urlfetch.fetch(url)
        logging.info(eventful_data_source)
        eventful_json_content= eventful_data_source.content
        logging.info(eventful_json_content)
        # eventful_dictionary= json.loads(eventful_json_content)
        # logging.info(eventful_dictionary)
    #    url_dictionary=eventful_dictionary['data'][0]['']['original']['url']
    #    goodurl={'niceurl': url}
        self.response.out.write(results_template.render({'url': unichr(eventful_json_content)}))
        '''

class AboutPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template= jinja_environment.get_template('templates/about.html')
        self.response.write(template.render())

class SavedPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template= jinja_environment.get_template('templates/saved_events.html')
        self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))

#####this is what we have

class FormHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/form.html')
        self.response.write(template.render())

class MapHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/map.html')
        self.response.write(template.render())

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = User(name=self.request.get('name'), email=self.request.get('email'), number = self.request.get('number'))
        key = user.put()
        template = jinja_environment.get_template('templates/my_profile.html')
        user_info = {
            'name': key.get().name,
            'email': key.get().email,
            'number': key.get().number,
        }
        self.response.write(template.render(user_info))

def get_data(user):
    return {
        'name': user.name,
        'email': user.email,
        'number': user.number,
    }


def get_info(method, query):
    student_info = None

    if method == 'name':
        logging.info("we're looking for mir")
        moar_students = Student.query()
        for student in moar_students:
            if student.name == query:
                logging.info("found mur")
                student_info = get_data(student)

    if method == 'id':
        student = Student.get_by_id(int(query))
        if student:
            student_info = get_data(student)
    return student_info


class SearchHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/search.html')
        self.response.write(template.render())
    def post(self):
        template = jinja_environment.get_template('templates/student.html')
        query = self.request.get('query')

        method = self.request.get('which_one')
        student_info = get_info(method, query)

        if (student_info):
            self.response.write(template.render(student_info))
        else:
            self.response.write("No results found :( <br> Let me just show you all the students :) <br><br>")
            for student in Student.query():
                self.response.write(template.render(get_data(student)))
            self.response.write("<a href='/home'>Go back home</a> <br>")


class StudentHandler(webapp2.RequestHandler):
    def get(self):
        student_id = int(self.request.get('id'))
        student = Student.get_by_id(student_id)
        template = jinja_environment.get_template('templates/student.html')
        student_info = {
            'student_name': student.name,
            'school': student.school,
            'age': student.age,
        }
        self.response.write(template.render(student_info))




routes = [
    ('/', MainHandler),
    ('/about', AboutPage),
    ('/saved_events', SavedPage),
    ('/romeo', RomeoHandler),
    ('/my_profile', FormHandler),
    ('/map', MapHandler),
    ('/form', FormHandler),
    ('/my_profile', ProfileHandler),
]

app = webapp2.WSGIApplication(routes, debug=True)

jinja_environment= jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
