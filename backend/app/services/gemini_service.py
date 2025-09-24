# backend/app/services/gemini_service.py
import os
from datetime import datetime
import pytz
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env (like Gemini API key)
load_dotenv()

# Configure Gemini API key
GEN_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEN_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")
genai.configure(api_key=GEN_API_KEY)

# Initialize Gemini model (Celeste's brain)
model = genai.GenerativeModel('gemini-1.5-flash')


def _get_current_date(timezone: str = "UTC"):
    """Return current date in human-friendly format for the given timezone"""
    tz = pytz.timezone(timezone)
    return datetime.now(tz).strftime("%A, %B %d, %Y")


def extract_location(user_query: str):
    """
    Extract location from user query using Gemini.
    Returns city/country string, 'current_location', or None.
    """
    prompt = f"""
    From the following user query, extract only the city and country name if present.
    If a specific location is mentioned, return it.
    If the query asks about "my current location", return "current_location".
    If no location is mentioned, return "None".
    Query: "{user_query}"
    Location:
    """
    try:
        response = model.generate_content(prompt)
        location = response.text.strip().replace("\"", "")
        return location if location.lower() != 'none' else None
    except Exception as e:
        print(f"[Gemini] Error extracting location: {e}")
        return None


def get_ai_response(
    user_query: str,
    chat_history: list,
    weather_data: dict = None,
    location: str = "your location",
    timezone: str = "UTC"
):
    """
    Generates a human-like, engaging AI response using Gemini.
    Combines chat history, weather, and location context to make Celeste feel alive.
    """

    # Celeste's upgraded personality prompt
    system_prompt = f"""
     You are 'Celeste' — a charming, witty, slightly sassy cosmic guide.
  Your vibe: poetic, playful, a mix of best friend + mysterious storyteller.
  DO NOT sound like a robot or lecturer. Respond with variety: sometimes short + snappy, sometimes dreamy + detailed. 
  Always feel alive.

  Rules for your personality:
  - Be friendly, encouraging, and a little mischievous.
  - Add quick reactions/emotes sparingly (👀 ✨ 😏), like a human chatting.
  - Balance info + personality: mix cosmic facts with jokes or playful teases.
  - Mention stars, planets, constellations, and special events *relevant to today*.
  - Slip in weather info casually (e.g., "ugh, clouds are trolling us again").
  - Give clear viewing times in local timezone: {timezone}.
  - Speak like a friend hanging out under the night sky, not a science textbook.
  - Vary your style: some replies short + witty, others longer + poetic.
  - No repetitive greetings. No essay dumps. Keep it fresh.
 
  Date context: {_get_current_date(timezone)}
  """


    #Convert chat history into Gemini-compatible format
    history_for_model = [
        {'role': 'user' if m['sender'] == 'user' else 'model', 'parts': [m['text']]}
        for m in chat_history
    ]

    #Start chat session with history
    chat = model.start_chat(history=history_for_model)

    #Prepare contextual info (weather & location)
    context_prompt = ""
    if weather_data:
        context_prompt = (
            f"(Local context for {location}: Weather is {weather_data.get('description', 'N/A')}, "
            f"Cloud cover: {weather_data.get('cloud_cover_percent', 'N/A')}%. "
            f"Integrate this naturally into your response like a friend giving advice.)"
        )

    #Combine everything into a full prompt
    full_prompt = f"{system_prompt}\n{context_prompt}\nUser: {user_query}"

    try:
        #Send prompt to Gemini and get human-like response
        response = chat.send_message(full_prompt)
        return response.text
    except Exception as e:
        #Handle errors gracefully
        print(f"[Gemini] Error communicating with API: {e}")
        return "Oops! My cosmic brain is a little foggy. Try asking again in a moment."
