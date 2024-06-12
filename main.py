from handling import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'
csrf = CSRFProtect(app)

# Import API keys as environment variables
gmapsApiKey = "AIzaSyDuFOYPcjJm8bCyqdnzULtGXcKv08BMd4c"
openAiApiKey = os.environ["openAiApiKey"]
client = OpenAI(api_key=openAiApiKey)
mapClient = googlemaps.Client(gmapsApiKey)
suggested_places = []
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

# Class definition for a generic user class. Will be used to store user info when a user is created
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
            print("==Invalid location specified. User not created.")
            return None

class SuggestedPlace:
    def __init__(self, name, location, placetype, rating, image):
        self.name = name
        self.location = location
        self.placetype = placetype
        self.rating = rating
        self.image = image

    def __str__(self):
        return f"Name: {self.name}, Location: {self.location}, Placetype: {self.placetype}, Rating: {self.rating}, Image: {self.image}"

# OpenAI API call function
def chatGpt_call_openai(prompt, api_key):
    completion = client.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages = [
            {'role': 'user', 'content': prompt}
        ],
        temperature = 0  
    )
    return eval(completion.choices[0].message.content)

# Creates a list of place_types compatible with gmaps API from a list of words (calls GPT)
def chatGpt_createPlaceTypesFromUser(user):
    prompt = (
        f"You are assisting in an app. Given a user's preferences and budget, "
        f"return a list of Google Maps place types (very important that they are PLACE TYPES) that fit the requirements. Return only an array, with no newlines or other text. These places are going to be used to plan a {user.outing_type}. "
        f"The user's hobbies are {user.hobbies} and the user's preferences are {user.preferences}, the user's budget is {user.budget}. "
        f"You must return 5 place types. Return random ones if you can't. It MUST be five."
    )
    user.placetypes = chatGpt_call_openai(prompt, openAiApiKey)
    print("==User placetypes fetched successfully: ", user.placetypes)
    return user.placetypes

def find_places(lat, lng, types, radius=2000):
    all_places = []
    for place_type in types:
        places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type={place_type}&key={gmapsApiKey}"
        response = requests.get(places_url)
        places_data = response.json()

        if places_data['status'] == 'OK':
            for place in places_data['results']:
                all_places.append({
                    'name': place['name'],
                    'address': place['vicinity'],
                    'rating': place.get('rating', 'N/A'),
                    'type': place_type,
                    'photo': place['photos'][0]['photo_reference'] if place.get('photos') else None
                })
        else:
            print(f"Error in fetching nearby places of type {place_type}: {places_data['status']}")
    return all_places

def gMaps_getSuitablePlacesFromUser(user):
    # Generate place types from user's preferences
    placetypes = chatGpt_createPlaceTypesFromUser(user)  
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

    print("==Keywords being generated:==")
    for placetype in placetypes:
        print(placetype)
        response = mapClient.places_nearby(
            location=user.coordinates(),
            radius=user.radius,
            type=placetype,
            min_price=min_price,
            max_price=max_price
        )
        print("==Gmaps API responded: ", response)
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
                # Create a new instance of SuggestedPlace
                new_place = SuggestedPlace(
                    name=place['name'],
                    location=place['location'],
                    placetype=placetype,
                    rating=place['rating'],
                    image=photo_url
                )
                places.append(new_place)
    print("==End of keywords==")
    return places

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

## Logic loop starts here :3
# App routing
@app.route('/')
def index():
    return render_template('index.html')

# Define a route to handle form submission and create the user object
@app.route('/register', methods=['POST'])
def register():
    print('==Form initialized successfully')
   
    # Extract form data
    username = request.form['username']
    address = request.form['address']
    radius = request.form['radius']
    hobbies = request.form['hobbies']
    preferences = request.form['preferences']
    budget = request.form['budget']
    outing_type = request.form['outing_type']  # New form field
   
    print('==Data fetched from form: ', [username, address, radius, hobbies, preferences, budget, outing_type])
    # Create a User object
    user = User(username, address, radius, hobbies, preferences, budget, outing_type)
    print('==User object created successfully : ', user.__dict__, ' stored as: ', user)
   
    # Convert user info to workable data (Google API placetypes)
    user.preferences = chatGpt_createPlaceTypesFromUser(user)
    print('==User preferences updated successfully : ', user.__dict__)
   
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
        radius=user_data['radius'],
        hobbies=user_data['hobbies'],
        preferences=user_data['preferences'],
        budget=user_data['budget'],
        outing_type=user_data['outing_type']
    )
   
    # Call the function to get suggested places
    suggested_places = gMaps_getSuitablePlacesFromUser(user)
    print('==Place suggestions generated successfully: ', len(suggested_places), ' places generated, ', suggested_places)
   
    # Pass the list of suggested places to the template
  
    return render_template('success.html', suggested_places=suggested_places)


@app.route('/selection', methods=['POST'])
def selection():
    selected_places = []
    for place in suggested_places:
        if request.form.get(place.name):
            selected_places.append(place)
    if len(selected_places) >= 3:
        session['selected_places'] = selected_places
        return redirect('/presenter')
    return redirect('/success')

@app.route('/presenter')
def presenter():
    selected_places = session.get('selected_places')
    if not selected_places:
        return redirect('/success')
    return render_template('presenter.html', selected_places=selected_places)
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
