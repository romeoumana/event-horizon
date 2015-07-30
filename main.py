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
import urllib
import unicodedata


from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb

from google.appengine.ext import vendor

# Add any libraries installed in the "lib" folder.
vendor.add('lib')

import httplib2
import simplejson
import eventful

class Person(ndb.Model):
    name = ndb.StringProperty(required=True)
    userID = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    number = ndb.StringProperty() # change to int property later
    bio = ndb.TextProperty()
    # events = ndb.StructuredProperty(Event, repeated=True)



class Event(ndb.Model):
    name = ndb.StringProperty()
    place = ndb.StringProperty()
    description = ndb.TextProperty()
    address = ndb.StringProperty()
    city = ndb.StringProperty()
    region = ndb.StringProperty()
    zip_code = ndb.StringProperty()
    country = ndb.StringProperty()
    place_url = ndb.StringProperty()
    start_time = ndb.StringProperty()
    frequency = ndb.StringProperty()
    # location = ndb.StringProperty(required=True)
    lat_lon = ndb.FloatProperty(repeated=True)
    # pictures = ndb.BlobProperty(required=True, repeated=True)

    # people = ndb.StructuredProperty(Person, repeated=True)


class PersonEvent(ndb.Model):
    person = ndb.KeyProperty(Person)
    event = ndb.KeyProperty(Event)

class RomeoHandler(webapp2.RequestHandler):
    def get(self):
        template= jinja_environment.get_template('templates/romeo.html')
        self.response.write(template.render({'results': "no swag"}))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template= jinja_environment.get_template('templates/sign_in.html')
        self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
        people = Person.query()
        if user:
            for person in people:
                if person.userID == user.user_id():
                    self.redirect('/home')
                    return
        if user:
            self.redirect('/create_profile')

class Home(webapp2.RequestHandler):
    def get(self):

        # deletes everything on datastore
        # people = Event.query()
        # for person in people:
        #     person.key.delete()
        # people = Person.query()
        # for person in people:
        #     person.key.delete()
        # people = PersonEvent.query()
        # for person in people:
        #     person.key.delete()



        user = users.get_current_user()
        if user:
            template= jinja_environment.get_template('templates/home.html')
            self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())

    def post(self):
        #!/usr/bin/env python
        api = eventful.API('P39qwcnBXLTHTnP3',cache=None)
        # api = eventful.API('test_key', cache=None)
        events = api.call('/events/search', q= self.request.get('query', default_value='music'), l=self.request.get('city', default_value='boston')) #later will be self.request.get('city')
        # logging.info(events)
        result_template= jinja_environment.get_template('templates/result.html')
        result=""
        if int(events['page_count']) > 0:

            for event in events['events']['event']:
                # logging.info(event['title'])
                # logging.info(event['venue_name'])
                # logging.info(event['description'])
                # logging.info(event['venue_address'])
                # logging.info(event['city_name'])
                # logging.info(event['region_name'])
                # logging.info(event['postal_code'])
                # logging.info(event['country_abbr'])
                # logging.info(event['venue_url'])
                # logging.info(event['start_time'])
                # logging.info(event['recur_string'])
                # logging.info(event['latitude'])
                # logging.info(event['longitude'])


                next_event = Event(name = event['title'],
                                    place = event['venue_name'],
                                    description= event['description'],
                                    address = event['venue_address'],
                                    city= event['city_name'],
                                    region = event['region_name'],
                                    zip_code= event['postal_code'],
                                    country = event['country_abbr'],
                                    place_url= event['venue_url'],
                                    start_time = event['start_time'],
                                    frequency= event['recur_string'],
                                    lat_lon = [float(event['latitude']), float(event['longitude'])]
                                    # pictures[0]= event['description'],
                                    )
                next_event = next_event.put()
                event_id = str(next_event.id())
                # logging.info('========================== EVENT ID')
                # logging.info(event_id)
                next_event = next_event.get()
                # logging.info(next_event.name)
                # logging.info(next_event.place)
                # logging.info(next_event.description)
                # logging.info(next_event.address)
                # logging.info(next_event.city)
                # logging.info(next_event.region)
                # logging.info(next_event.zip_code)
                # logging.info(next_event.country)
                # logging.info(next_event.place_url)
                # logging.info(next_event.start_time)
                # logging.info(next_event.frequency)
                # logging.info(next_event.lat_lon)

                result+= "<a href='/event?id=" + event_id + "'>" + event['title'] + " at " + event['venue_name'] + "</a><br>" # "<a href='/event?id=%s> %s at %s</a><br>" % (event_id, event['title'], event['venue_name'])

            self.response.write(result_template.render({"results": result}))
        else:
            self.response.write(result_template.render({"results": "None"}))

class AboutPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template_data = {'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}
            template= jinja_environment.get_template('templates/about.html')
            self.response.write(template.render(template_data))
        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())

class SavedHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template= jinja_environment.get_template('templates/saved_events.html')
            self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())
#####this is what we have

class FormHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template = jinja_environment.get_template('templates/form.html')
            self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())

class MapHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template = jinja_environment.get_template('templates/map.html')
            self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_data = {'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}
        if user:
            template = jinja_environment.get_template('templates/my_profile.html')
            people = Person.query().fetch()
            # logging.info(people)
            for person in people:
                if person.userID == user.user_id():
                    template_data['name'] = person.name #unicodedata.normalize('NFKD', person.name).encode('ascii','ignore')
                    template_data['email'] = user.email()
                    template_data['bio'] = person.bio
                    break
            relationships = PersonEvent.query().fetch()
            template_data['results'] = ""
            for relationship in relationships:
                if relationship.person.get().name == template_data['name']:
                    event = relationship.event.get()
                    event_id = str(event.key.id())

                    template_data['results'] += "<a href='/event?id=" + event_id + "'>" + event.name + " at " + event.place + "</a><br>"

            self.response.write(template.render(template_data))

            # line below may never execute because user will always have a profile at this point
            # only uncomment line below if Google users get in without a TEH profile
            # self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))

        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())

class CreateProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template = jinja_environment.get_template('templates/profile_form.html')
        self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
    def post(self):
        user = users.get_current_user()
        person = Person(name = self.request.get('person_name'), userID = user.user_id(), email = user.email(), number = '305-305-3053', bio = self.request.get('bio'))
        person.put()
        self.redirect('/home')

class EventHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template = jinja_environment.get_template('templates/event.html')
        template_data = {'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}
        event = Event.get_by_id(long(self.request.get('id')))



        template_data['name'] = event.name
        template_data['place'] = event.place
        template_data['description'] = event.description
        template_data['address'] = event.address
        template_data['city'] = event.city
        template_data['region'] = event.region
        template_data['zip_code'] = event.zip_code
        template_data['country'] = event.country
        template_data['start_time'] = event.start_time
        template_data['frequency'] = event.frequency
        # if event.frequency == None:
        #     template_data['frequency'] = event.frequency

        self.response.write(template.render(template_data))

    def post(self):
        user = users.get_current_user()
        people = Person.query()
        for person in people:
            if person.userID == user.user_id():
                person_key = person.key
                break
        event_key = Event.get_by_id(long(self.request.get('id'))).key
        attender = PersonEvent(person = person_key, event = event_key)
        relationships = PersonEvent.query()
        logging.info(relationships)
        match = False
        for relationship in relationships:

            logging.info('person_key.id()')
            logging.info(person_key.id())

            logging.info('relationship.person.id()')
            logging.info(relationship.person.id())

            logging.info('event_key.id()')
            logging.info(event_key.id())

            logging.info('relationship.event.id()')
            logging.info(relationship.event.id())
            if (person_key.id() == relationship.person.id() and event_key.id() == relationship.event.id()):
                match = True
                logging.info("there is a match in relationships! noswag")
        if not match:
            attender.put()
            logging.info("no relationship match swag")
        self.redirect('/my_profile')


routes = [
    ('/',MainHandler),
    ('/home', Home),
    ('/about', AboutPage),
    ('/saved', SavedHandler),
    ('/romeo', RomeoHandler),
    ('/map', MapHandler),
    ('/form', FormHandler),
    ('/my_profile', ProfileHandler),
    ('/create_profile', CreateProfileHandler),
    ('/event', EventHandler)
]

app = webapp2.WSGIApplication(routes, debug=True)

jinja_environment= jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
