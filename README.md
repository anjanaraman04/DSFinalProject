# DSFinalProject

A Flask REST API that answers questions about historical natural disasters and real time weather using a locally cleaned CSV and the Open‑Meteo public API.

# Features 
- Python‑based ETL script converts the raw Kaggle dataset to a compact CSV
- **/chat** `POST` Route
  - `deadliest <year>` → highest‑fatality event for that year
  - `count <type> <country> <start>-<end>` → event count in range
  - `weather <lat> <lon>` → real‑time temperature, wind, precipitation

# Running the Bot Locally 
1. Clone repository
2. Enter virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
3. Install dependencies `pip3 install...`
4. Download Kaggle CSV and place it in the repository https://www.kaggle.com/datasets/brsdincer/all-natural-disasters-19002021-eosdis?resource=download
5. Run etl.py ONCE `python3 etl.py`
6. Start the flask app `python3 app.py` and visit http://127.0.0.1:5000

# Running remotely/through Browser
POST Method link: http://34.86.33.221:5000/chat  

Browser link (Skeleton front end): http://34.86.33.221:5000/  

Note: Front end makes POST calls to the link above to retrieve information  

Optionally run in a seperate terminal commands such as...
```
curl -X POST localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"deadliest 2010"}'

curl -X POST localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"weather 40.7 -74.0"}'
```




