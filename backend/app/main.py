from flask import Flask, request, jsonify
from flask_cors import CORS
from .services import gemini_service, weather_service

app = Flask(__name__) #initializes the backend.
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}) #allows only frontend at localhost:3000 to call routes starting with /api/.

@app.route('/api/ask', methods=['POST'])
def ask_agent():  #When frontend sends POST request to /api/ask, this function runs.
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Query not provided"}), 400 #Checks if query exists; if not, returns HTTP 400 (bad request) with error.

    user_query = data['query'] #what the user asked.
    chat_history = data.get('history', []) # Get the history from the request
    user_lat = data.get('latitude')
    user_lon = data.get('longitude')
    
    weather_data = None
    location_name = "your location"
    location_query = None

    explicit_location = gemini_service.extract_location(user_query)

    #Decides which location to use
    if explicit_location and explicit_location != "current_location":
        location_query = explicit_location
        location_name = explicit_location
    elif user_lat and user_lon:
        location_query = f"{user_lat},{user_lon}"
        
    if location_query:
        _, weather_data = weather_service.get_weather_and_location_data(location_query) #Calls the weather service using location_query.

    # Pass the history to the Gemini service
    ai_response = gemini_service.get_ai_response(user_query, chat_history, weather_data, location_name)

    return jsonify({"response": ai_response})

if __name__ == '__main__': #Runs the Flask server at localhost:5001.
    app.run(debug=True, port=5001)



#Flask is a lightweight web framework for Python. 
#It Lets Python talk to the web (HTTP requests and responses).
# Flask → the main web framework object to create the app.
# request → lets you access incoming HTTP request data (like JSON from frontend).
# jsonify → converts Python objects (dicts, lists) into JSON to send back to the frontend.