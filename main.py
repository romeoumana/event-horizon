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

from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Student(ndb.Model):
    name = ndb.StringProperty(required=True)
    school = ndb.StringProperty(required=True)
    age = ndb.IntegerProperty(required=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('template/home.html')
        self.response.write(template.render())

class EnterHandler(webapp2.RequestHandler):
    def get(self):
        student = Student(name="Romeo", school = "Stanford University", age=18)
        student.put()
        template = jinja_environment.get_template('template/student.html')
        name = student.name
        school = student.school
        age = student.age
        student_info = {
            'student_name': student.name,
            'school': student.school,
            'age': student.age
            }
        self.response.write(template.render(student_info))

class FormHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('template/form.html')
        self.response.write(template.render())

    def post(self):
        student = Student(name=self.request.get('name'), school=self.request.get('school'), age = int(self.request.get('age')))
        key = student.put()
        template = jinja_environment.get_template('template/student.html')
        student_info = {
            'student_name': key.get().name,
            'school': key.get().school,
            'age': key.get().age,
        }
        self.response.write(template.render(student_info))

def get_data(student):
    return {
        'student_name': student.name,
        'school': student.school,
        'age': student.age,
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
        template = jinja_environment.get_template('template/search.html')
        self.response.write(template.render())
    def post(self):
        template = jinja_environment.get_template('template/student.html')
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
        template = jinja_environment.get_template('template/student.html')
        student_info = {
            'student_name': student.name,
            'school': student.school,
            'age': student.age,
        }
        self.response.write(template.render(student_info))
        
routes = [
    ('/home', MainHandler),
    ('/enter', EnterHandler),
    ('/form', FormHandler),
    ('/search', SearchHandler),
    ('/student', StudentHandler),
    ('/.*', MainHandler),
]
app = webapp2.WSGIApplication(routes, debug=True)
