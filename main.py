import flask
from flask import Flask, render_template, request, redirect, url_for, session
import flask_wtf
import googlemaps
import pandas as pd  
from pprint import pprint
from openai import OpenAI
import os
import math
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
csrf = CSRFProtect(app)

#app routing
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/planner')
def planner():
    return render_template('planner.html')
    
@app.route('/suggestions')
def suggestions():
    return render_template('suggestions.html')


#imports api keys as environment variables

gmapsApiKey = os.environ['gmapsApiKey']
openAiApiKey = os.environ['openAiApiKey']

client = OpenAI(api_key = openAiApiKey)
mapClient = googlemaps.Client(gmapsApiKey)






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
def chatGpt_call_openai(prompt, api_key):
  completion = client.chat.completions.create( 
    model = 'gpt-3.5-turbo',
    messages = [ 
      {'role': 'user',
      'content': prompt}
    ],
    temperature = 0  
  )
  return completion.choices[0].message.content

#creates a list of place_types compatible with gmaps api from a list of words (calls gpt)
#takes in a user object
#returns list of place_types

def chatGpt_createPlaceTypesFromUser(user):
  prompt = (
      f"You are assisting in an app. Given a user's preferences and budget, "
      f"return a list of googlemaps API place types that fit the requirements. Return only an array, with no newlines or other text."
      f"The user's preferred activities are {user.activities}. The user's budget is {user.budget}."
  )
  return chatGpt_call_openai(prompt, openAiApiKey)



def gMaps_locationSearch(_location, _radius, _placeType, _priceLevel):
  
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
def addressToCoordinates(address):
    return [mapClient.geocode(address)[0]['geometry']['location'].get('lat'), 
    mapClient.geocode(address)[0]['geometry']['location'].get('lng')]

def gMaps_createListOfSuitablePlaces(address,radius, placetypes, budget):
    coordinates = addressToCoordinates(address)
    return gMaps_locationSearch(coordinates, radius, placetypes, budget)

def gMaps_possiblePlaces(address):
  return mapClient.places_nearby(location = [43.6532, -79.3843], radius = 10000)
print(gMaps_possiblePlaces("51 Duning Ave, Aurora, ON, L4G 0A1"))

def createSpecificBudget(budget):
  if budget > 1000:
     result = 3
  else:
    result = math.log(10, budget)



print(addressToCoordinates(johnDoe.address))
print(chatGpt_createPlaceTypesFromUser(johnDoe))

