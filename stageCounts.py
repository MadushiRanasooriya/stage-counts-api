import requests
from flask import Flask, jsonify
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}"
}

def get_deals():
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    headers = HEADERS
    params = {
        "properties": "dealstage",
        "limit": 100
    }

    all_deals = []

    while True:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        all_deals.extend(data.get("results", []))

        if "paging" in data and "next" in data["paging"]:
            params["after"] = data["paging"]["next"]["after"]
        else:
            break

    return all_deals

def get_stage_labels():
    url = "https://api.hubapi.com/crm/v3/pipelines/deals"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    
    stage_map = {}
    for stage in data["results"][0]["stages"]:
        stage_map[stage["id"]] = stage["label"]
    return stage_map

@app.route("/")
def home():
    deals = get_deals()
    stage_labels = get_stage_labels()
    stage_counts = {}

    for deal in deals:
        stage_id = deal["properties"]["dealstage"]
        stage_name = stage_labels.get(stage_id, "Unknown")
        stage_counts[stage_name] = stage_counts.get(stage_name, 0) + 1

    
    # stage_counts_combined = {
    #     "New Leads": stage_counts.get("NEW", 0)  + stage_counts.get("LOST - RENEGOTIATION", 0),
    #     "Appointment": stage_counts.get("APPOINTMENT SCHEDULED", 0),
    #     "Offer": stage_counts.get("OFFER SENT", 0),
    #     "Negotiation": stage_counts.get("NEGOTIATION OF OFFER", 0),
    #     "Customers": stage_counts.get("DEAL CLOSED - WON", 0),
    #     "Target Customers": 12
    # }

    # labels = list(stage_counts_combined.keys())
    # counts = list(stage_counts_combined.values())
    
    return jsonify(stage_counts)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

