
import csv
import requests
import time
import json


def read_city_names():
    # TODO: Extract City Names List
    file_path = "city_names_germany.txt"
    city_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            city_list.append(line.strip())
    return city_list[0:101]

def save_results(result_json):
    with open('Optiker_info.csv', 'a+', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        row = [
            result_json['city'],
            result_json['name'],
            result_json['rating'],
            result_json['reviews'],
            result_json['address'],
            result_json['phone'],
            result_json['website']
        ]
        writer.writerow(row)
def get_places_info(city):
    # for page in range(0, 101, 20):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"unabhängiger Optiker {city}",
        "key": google_maps_api_key,
        # "start": page
    }

    # Send the request and get the response
    response = requests.get(url, params=params)
    data = json.loads(response.text)

    # Extract the place IDs from the response
    place_ids = []
    for result in data["results"]:
        place_ids.append(result["place_id"])

    # Check if there is a next page token
    while "next_page_token" in data:
        time.sleep(2)
        # Set up the API endpoint and parameters for the next page
        params = {
            "pagetoken": data["next_page_token"],
            "key": google_maps_api_key
        }

        # Send the request and get the response
        response = requests.get(url, params=params)
        data = json.loads(response.text)

        # Extract the place IDs from the response
        for result in data["results"]:
            place_ids.append(result["place_id"])

    # Set up the API endpoint and parameters for each place ID
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    results = []
    for place_id in place_ids:
        params = {
            "place_id": place_id,
            "fields": "name,rating,user_ratings_total,formatted_address,formatted_phone_number,website",
            "key": google_maps_api_key
        }

        # Send the request and get the response
        response = requests.get(url, params=params)
        data = json.loads(response.text)

        # Extract the desired information from the response
        result = {
            "city": city,
            "name": data["result"]["name"],
            "rating": data["result"].get("rating", "N/A"),
            "reviews": data["result"].get("user_ratings_total", "N/A"),
            "address": data["result"].get("formatted_address", "N/A"),
            "phone": data["result"].get("formatted_phone_number", "N/A"),
            "website": data["result"].get("website", "N/A")
        }
        results.append(result)

    # Print the results
    print(f"found {len(results)} in city {city}")
    for result in results:
        print(result)
        save_results(result)



google_maps_api_key = "YOU_API_KEY"
city_list = read_city_names()

for city in city_list:
    get_places_info(city)


