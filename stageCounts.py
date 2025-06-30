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
        "properties": "dealstage,amount,dealname,closedate,createdate",
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

    deals_data = []

    for deal in deals:
        props = deal.get("properties", {})
        stage_id = props.get("dealstage", "Unknown")
        stage_name = stage_labels.get(stage_id, "Unknown")

        deal_entry = {
            "dealname": props.get("dealname", "Unnamed Deal"),
            "dealstage": stage_name,
            "amount": props.get("amount", 0),
            "closedate": props.get("closedate", "N/A"),
            "createdate": props.get("createdate", "N/A")
        }

        deals_data.append(deal_entry)
    
    return jsonify(deals_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
