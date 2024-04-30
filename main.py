import flask
from flask import Flask, render_template, request, redirect, url_for, session
import flask_wtf
import googlemaps
import pandas as pd  
from pprint import pprint
from openai import OpenAI
import os
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
csrf = CSRFProtect(app)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/planner')
def planner():
    return render_template('planner.html')
    
@app.route('/suggestions')
def suggestions():
    return render_template('suggestions.html')




GmapsApiKey = os.environ['gmapsApiKey']
openAiApiKey = os.environ['openAiApiKey']

client = OpenAI(api_key = openAiApiKey)
mapClient = googlemaps.Client(GmapsApiKey)





#class definition for a generic user class. Will be used to store user info when a user is created
#class definition for a generic user class. Will be used to store user info when a user is created
class User:
  def __init__(self, name, lastName, email, phoneNumber, address, city, password, currentRadius, preferences, activities, budget):

    self.name = name
    self.lastName = lastName
    self.email = email
    self.phoneNumber = phoneNumber
    self.address = address
    self.city = city
    self.currentRadius = currentRadius

    self.password = password
    self.preferences = preferences
    self.activities = activities
    self.budget = budget



#openai api call function
#calls the openai api, takes in a prompt, api key
#returns the unparsed completion result
def call_openai(prompt, api_key):
  completion = client.chat.completions.create( 
    model = 'gpt-3.5-turbo',
    messages = [ 
      {'role': 'user', 'content': prompt}
    ],
    temperature = 0  
  )
  return completion.choices[0].message.content

def createPlaceTypeIdeas(user):
  prompt = (
      f"You are assisting in an app. Given a user's preferences and budget, "
      f"return a list of googlemaps API place types that fit the requirements. Return only an array, with no newlines or other text."
      f"The user's preferred activities are {user.activities}. The user's budget is {user.budget}."
  )
  return call_openai(prompt, openAiApiKey)



def locationSearch(_location, _radius, _placeType, _priceLevel):
  
  return mapClient.places_nearby(
    location = _location,
    radius = _radius,
    type = _placeType,
    price_level = _priceLevel
  )
 
johnDoe = User(
  name = 'John',
  lastName = 'Doe',
  email = 'tugrp@example.com',
  phoneNumber = '123-456-7890',
  address = "51 Duning Ave, Aurora, ON, L4G 0A1",
  city = 'Aurora',
  currentRadius = 10000,
  password = "password",
  preferences = ['chinese food', 'indoors','outdoors'],
  activities= ['hiking','eating','museum'],
  budget = 100



)

def parseGmapsApiResponse(response):
  places = []
  for place in response['results']:
    places.append[place['name'], place['vicinity'], place['place_id']]
  return places

def possiblePlaces(address):
  return mapClient.places_nearby(location = [43.6532, -79.3843], radius = 10000)
print(possiblePlaces("51 Duning Ave, Aurora, ON, L4G 0A1"))

print(createPlaceTypeIdeas(johnDoe))
