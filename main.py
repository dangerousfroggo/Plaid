from flask import Flask, render_template, request, redirect, url_for, session

import googlemaps
import pandas as pd  
from pprint import pprint
import openai
import os
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/planner')
def planner():
    return render_template('planner.html')



GmapsApiKey = "AIzaSyDFP1V6wDl-Faua2ljubPUsTPNrOuJGwEk"
openAiApiKey = my_secret = os.environ['openAiKey']


mapClient = googlemaps.Client(GmapsApiKey)



#testResponse = mapClient.geocode(testAddress)
#locationRadiusResult = mapClient.places_nearby(location = '43.95197153319961, -79.45002830396922', radius = 10000, open_now = False, type = 'restaurant')


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



def locationSearch(userLocation, userRadius, placeType, keyWords):
  response = mapClient.places_nearby(location = userLocation, radius = userRadius, open_now = False, type = placeType, keyword = keyWords)
  return response


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