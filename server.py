#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
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
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, redirect, jsonify
import json
from random import randint
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.space = dict()

        # A dictionary of updates. Key is client provided id (yes I am aware this isn't secure,
        # it's a drawing app), values are dictionaries of entity updates, a subset of world.
        self.queues = dict()

        self.clear()

    def update(self, entity, key, value):
        entry = self.space.get(entity, dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        """
        Sets the given entity to a specific value.
        Informs all queues of the update
        """
        self.space[entity] = data

        # Append this update to every queue
        for queue in self.queues:
            self.queues[queue][entity] = data

        # for queue in self.queues:
        #     queue[entity] = data

    # def pop_queue(self, queue):
    #     """
    #     Gets the specified queue, then clears it
    #     """
    #     for

    def clear(self):
        self.space = dict()
        self.queues = dict()

    def get(self, entity):
        return self.space.get(entity, dict())

    def world(self):
        return self.space

    def queue(self, queue_id):
        if queue_id in self.queues:
            result = self.queues[queue_id]
            self.queues[queue_id] = dict()
            return result
        else:
            return dict()

    def register_queue(self, queue_id):
        """
        Create a queue with the given queue_id
        """
        if queue_id not in self.queues:
            self.queues[queue_id] = dict()

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}'

myWorld = World()

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    return redirect('static/index.html', 302)

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    post_vars = flask_post_json()

    myWorld.set(entity, post_vars)
    return jsonify(myWorld.get(entity))

@app.route("/world", methods=['POST','GET'])
def world():
    '''you should probably return the world here'''
    return jsonify(myWorld.world())

@app.route("/entity/<entity>")
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    return jsonify(myWorld.get(entity))

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.clear()
    return jsonify(myWorld.world())

@app.route("/get_updates/<queue_id>", methods=['POST', 'GET'])
def get_queue(queue_id):
    '''
    Get the queue of updates waiting for this specific id
    Also clears the queue
    '''
    return jsonify(myWorld.queue(queue_id))

@app.route("/register_queue", methods=['POST'])
def register_queue():
    '''
    Register a queue into the system
    '''
    post_vars = flask_post_json()
    if 'uuid' in post_vars:
        myWorld.register_queue(post_vars['uuid'])
    return jsonify({'success': 'Queue created'})

# @app.route('/register/<queue_id>', methods=['GET'])
# def register_queue(queue_id):
#     """
#     Registers a queue for this id in the system
#     """
#     myWorld.register_queue(queue_id)

if __name__ == "__main__":
    app.run()
