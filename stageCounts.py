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
    params = {
        "properties": "dealstage",
        "limit": 100
    }

    all_deals = []
    while True:
        response = requests.get(url, headers=HEADERS, params=params)
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

def get_companies():
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    params = {
        "properties": "industry",
        "limit": 100
    }

    all_companies = []
    while True:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        all_companies.extend(data.get("results", []))

        if "paging" in data and "next" in data["paging"]:
            params["after"] = data["paging"]["next"]["after"]
        else:
            break

    return all_companies

@app.route("/deal-stages")
def deal_stages():
    deals = get_deals()
    stage_labels = get_stage_labels()
    stage_counts = {}

    for deal in deals:
        stage_id = deal["properties"]["dealstage"]
        stage_name = stage_labels.get(stage_id, "Unknown")
        stage_counts[stage_name] = stage_counts.get(stage_name, 0) + 1

    return jsonify(stage_counts)

@app.route("/industry-counts")
def industry_counts():
    companies = get_companies()
    industry_counts = {}

    for company in companies:
        industry = company["properties"].get("industry", "Unknown")
        industry_counts[industry] = industry_counts.get(industry, 0) + 1

    return jsonify(industry_counts)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
