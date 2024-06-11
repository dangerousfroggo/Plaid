from handling import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'
csrf = CSRFProtect(app)





#imports api keys as environment variables

gmapsApiKey = os.environ["gmapsApiKey"]
openAiApiKey = os.environ["openAiApiKey"]
client = OpenAI(api_key = openAiApiKey)
mapClient = googlemaps.Client(gmapsApiKey)

def addressToCoordinates(address):
    try:
        geocode_result = mapClient.geocode(address)
        if not geocode_result:
            return None
        location = geocode_result[0].get('geometry', {}).get('location', {})
        lat = location.get('lat')
        lng = location.get('lng')
        return [lat, lng]
    except Exception as e:
        print(f"==Error in geocoding: {e}")
        return None



#class definition for a generic user class. Will be used to store user info when a user is created
class User:
    def __init__(self, username, address, radius, hobbies, preferences, budget, outing_type, placetypes=[]):
        self.username = username
        self.address = address
        self.radius = radius
        self.hobbies = hobbies
        self.preferences = preferences
        self.budget = budget
        self.outing_type = outing_type  
        self.placetypes = placetypes
    def coordinates(self):
      geocodeResult = mapClient.geocode(self.address)
      if geocodeResult:
          location = geocodeResult[0]['geometry']['location']
          latitude = location['lat']
          longitude = location['lng']
          return (latitude, longitude)
      else:
          print("==invalid location specified. user not created ")
          return None

class suggestedPlace:
    def __init__(self,name,location,placetype, rating, image):
        self.name = name
        self.location = location
        self.placetype = placetype
        self.rating = rating
        self.image = image
    def __str__(self):
        return f"Name: {self.name}, Location: {self.location}, Placetype: {self.placetype}, Rating: {self.rating}, Image: {self.image}"




    

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
  return literal_eval(completion.choices[0].message.content)

#creates a list of place_types compatible with gmaps api from a list of words (calls gpt)
#takes in a user object
#returns list of place_types

def chatGpt_createPlaceTypesFromUser(user):
    prompt = (
        f"You are assisting in an app. Given a user's preferences and budget, "
        f"return a list of googlemaps API place types that fit the requirements. Return only an array, with no newlines or other text. These places are going to be used to plan a {user.outing_type}. "
        f"The user's hobbies are {user.hobbies} and the user's preferences are {user.preferences}, the user's budget is {user.budget}. "
        f"You must return 5 place tags. return random ones if you cant. it MUST be five."
    )
    user.placetypes = chatGpt_call_openai(prompt, openAiApiKey)
    print("==user placetypes fetched successfully: ", user.placetypes)
    return user.placetypes

def gMaps_getSuitablePlacesFromUser(user):
    placetypes = chatGpt_createPlaceTypesFromUser(user)
    if not user:
        return None  # or handle the error appropriately

    places = []
    budget = user.budget

    if budget == "20":
        min_price = 0
        max_price = 1
    elif budget == "50":
        min_price = 0
        max_price = 2
    elif budget == "100":
        min_price = 0
        max_price = 3
    else:
        min_price = 0
        max_price = 4
    print("==keywords being generated:== ")
    for i in range(0, len(placetypes)):
        
        keyword = placetypes[i]
        print(keyword)
        response = mapClient.places_nearby(
            location=user.coordinates(),
            radius=user.radius,
            keyword=keyword,
            min_price=min_price,
            max_price=max_price
        )

        parsed_results = parseGmapsResponse(response)

        for place in parsed_results:
            if place['name']:
                # Get the photo reference link
                if place.get('photo'):
                    photo_reference = place.get('photo', {}).get('photo_reference')
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={gmapsApiKey}"
                else:
                    photo_reference = None
                    photo_url = None
                # Create a new instance of suggestedPlace
                new_place = suggestedPlace(
                    name=place['name'],
                    location=place['location'],
                    placetype=keyword,
                    rating=place['rating'],
                    image=photo_url
                )
                places.append(new_place)
    print("==end of keywords==")
    return places



def getPlacePhoto(placeId,maxWidth,maxHeight):
    url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={maxWidth}&maxheight={maxHeight}&photoreference={placeId}&key={gmapsApiKey}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None

def parseGmapsResponse(response):
    parsed_results = []
    for place in response.get('results', []):
        place_info = {}
        place_info['name'] = place.get('name', 'N/A')
        place_info['place_id'] = place.get('place_id')
        place_info['types'] = place.get('types', [])
        place_info['rating'] = place.get('rating', 'N/A')
        place_info['location'] = place['geometry']['location']
        place_info['vicinity'] = place.get('vicinity')
        place_info['photo'] = place.get('photos')[0] if place.get('photos') else None
        parsed_results.append(place_info)
    return parsed_results





##logic loop starts here :3
#app routing



@app.route('/')
def index():
    return render_template('index.html')

# Define a route to handle form submission and create the user object
@app.route('/register', methods=['POST'])
def register():
    print('==form initialized successfully')
   
    # Extract form data
    username = request.form['username']
    address = request.form['address']
    radius = request.form['radius']
    hobbies = request.form['hobbies']
    preferences = request.form['preferences']
    budget = request.form['budget']
    outing_type = request.form['outing_type']  # New form field
    
    print('==data fetched from form: ', [username, address, radius, hobbies, preferences, budget,outing_type])
    # Create a User object
    user = User(username, address, radius, hobbies, preferences, budget, outing_type)
    print('==user object created successfully : ', user.__dict__, ' stored as: ', user)
    # Convert user info to workable data (Google API placetypes)
    user.preferences = chatGpt_createPlaceTypesFromUser(user)
    print('==user preferences updated successfully : ', user.__dict__)
    
    # Store user data in the session
    session['current_user'] = {
        'username': username,
        'address': address,
        'radius': radius,
        'hobbies': hobbies,
        'preferences': preferences,
        'budget': budget,
        'outing_type': outing_type
    }
    
    return redirect('/success')


@app.route('/success')
def success():
    user_data = session.get('current_user')
    if not user_data:
        return redirect('/')  # Redirect to the index page if user data is not found in the session
    
    # Create a User object using the user data
    user = User(
        username=user_data['username'],
        address=user_data['address'],
        radius=user_data['radius']*1000,
        hobbies=user_data['hobbies'],
        preferences=user_data['preferences'],
        budget=user_data['budget'],
        placetypes=user_data['preferences'],
        outing_type=user_data['outing_type']
    )
    
    # Call the function to get suggested places
    suggested_places = gMaps_getSuitablePlacesFromUser(user)

    print('==place suggestions generated successfully: ', len(suggested_places) , ' places generated, ', suggested_places)

    # Pass the list of suggested places to the template
    return render_template('success.html', suggested_places=suggested_places)

    


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)