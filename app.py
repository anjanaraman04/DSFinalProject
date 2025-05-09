import os, re, json
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai 



load_dotenv()                                      
DATA_FILE   = Path(__file__).parent / "data" / "DisastersCleaned.csv"
CURRENT_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
CLIMATE_URL = "https://climate-api.open-meteo.com/v1/climate"

genai.configure(api_key=os.environ["GEMINI_API_KEY"]) 
MODEL = genai.GenerativeModel("gemini-1.5-flash")        

try:
    DISASTERS = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    raise SystemExit(
        "ERROR: DisastersCleaned.csv not found. Run `python etl.py` first."
    ) from None


def deadliest_disaster(year: int) -> str:
    year_df = DISASTERS[DISASTERS["year"] == year]
    if year_df.empty: 
        raise LookupError("Information not available!")
    top_death_toll = year_df.sort_values("deaths", ascending=False).iloc[0]
    return f"The deadliest disaster in {year} was {top_death_toll.type.lower()} in {top_death_toll.country} with a number of {top_death_toll.deaths} deaths"

def count_events(disaster_type: str, country: str, start: int, end: int) -> str:
    dtype = DISASTERS["type"].str.contains(disaster_type, case = False)
    c = DISASTERS["country"].str.contains(country, case = False)
    s = DISASTERS["year"].between(start, end)
    mask = dtype & c & s
    number_of_events = mask.sum()
    return f"{number_of_events} {disaster_type} events were recorded in {country} from {start} to {end}"

def current_weather(lat: float, lon: float) -> str:
    params = {
        "latitude": lat,
        "longitude": lon, 
        "current": "temperature_2m,wind_speed_10m,precipitation"
    }
    data = requests.get(CURRENT_WEATHER_URL, params=params, timeout=10)
    data.raise_for_status()
    data = data.json()["current"]
    return f"The current temperature at {lat}, {lon}: {data["temperature_2m"]} Celcius, wind speeds of {data["wind_speed_10m"]} m/s, and  precipitation of {data["precipitation"]} mm/h."


def first_parse(query: str) -> str:
    query = query.strip()
    if m := re.match(r"deadliest\s+(\d{4})$", query, re.IGNORECASE):
        return deadliest_disaster(int(m.group(1)))
    if m := re.match(r"count\s+(\w+)\s+(\w+)\s+(\d{4})-(\d{4})$", query, re.IGNORECASE):
        dtype, country, start, end = m.groups()
        return count_events(dtype, country, int(start), int(end))
    if m := re.match(r"weather\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)",query, re.IGNORECASE):
        lat, lon = map(float, m.groups())
        return current_weather(lat, lon)
        
    raise ValueError("query does not match")

def ask_gemini(system_prompt: str, user_query: str) -> str:
    prompt = f"{system_prompt}\n\nUSER: {user_query}"
    try:
        return MODEL.generate_content(prompt).text.strip()
    except Exception as exc:
        raise RuntimeError(f"Gemini error: {exc}") from exc

def answer_prompt(query: str) -> str: 
    try:
        return first_parse(query)
    except ValueError:
        pass
    
    system_prompt = "Please answer the question using any data you can find on the internet about natural disasters. If the question is about current weather than answer accordingly using sources from the internet as well. PLEASE DISPLAY THE INFORMATION YOU FOUND."
    return ask_gemini(system_prompt, query)


app = Flask(__name__, template_folder="templates")

@app.get("/")
def home():
    """Serve the bare-bones UI."""
    return render_template("index.html")

@app.post("/chat")
def chat():
    try:
        user_msg = request.get_json(force=True).get("message", "").strip()
        if not user_msg:
            return jsonify(error="message field is required"), 400

        answer = answer_prompt(user_msg)
        return jsonify(answer=answer)

    except (LookupError, ValueError) as e:
        return jsonify(error=str(e)), 400
    except requests.RequestException as e:
        return jsonify(error=f"Weather API error: {e}"), 503
    except RuntimeError as e:                     
        return jsonify(error=str(e)), 503
    except Exception as e:
        app.logger.exception(e)
        return jsonify(error="Internal server error"), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)





