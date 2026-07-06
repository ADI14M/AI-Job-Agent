import os
import json
import requests
import uuid

def generate_locations():
    # We will use a public dataset of countries/cities or just a major world cities dataset.
    # A good open dataset for world cities: https://raw.githubusercontent.com/lutangar/cities.json/master/cities.json
    print("Downloading cities dataset...")
    url = "https://raw.githubusercontent.com/lutangar/cities.json/master/cities.json"
    r = requests.get(url)
    
    if r.status_code != 200:
        print("Failed to download cities. Using a fallback list.")
        cities_data = []
    else:
        cities_data = r.json()

    print(f"Loaded {len(cities_data)} cities.")
    
    locations = []
    processed_names = set()
    
    # Custom required locations and aliases mapping
    aliases = {
        "Bangalore": ["Bengaluru"],
        "Bengaluru": ["Bangalore"],
        "Bombay": ["Mumbai"],
        "Mumbai": ["Bombay"],
        "Madras": ["Chennai"],
        "Chennai": ["Madras"],
        "New York": ["NYC", "New York City", "NY"],
        "San Francisco": ["SF", "San Fran"],
        "Los Angeles": ["LA"],
        "Washington": ["DC", "Washington DC"],
        "United Kingdom": ["UK"],
        "United States": ["USA", "US", "United States of America"],
        "United Arab Emirates": ["UAE"]
    }
    
    # Always include Remote and Worldwide
    locations.append({
        "id": "remote",
        "city": "Remote",
        "country": "",
        "display": "Remote",
        "aliases": ["WFH", "Work from home"]
    })
    locations.append({
        "id": "worldwide",
        "city": "Worldwide",
        "country": "",
        "display": "Worldwide",
        "aliases": ["Global", "Anywhere"]
    })
    
    # To avoid 100,000+ cities slowing things down, let's filter to important ones.
    # We can keep cities with a known country.
    # The dataset has `name`, `country`
    count = 0
    for c in cities_data:
        name = c.get("name")
        country = c.get("country")
        
        # We want unique combinations of city + country
        key = f"{name}-{country}"
        if key in processed_names:
            continue
        processed_names.add(key)
        
        display = f"{name}, {country}" if country else name
        
        city_aliases = []
        if name in aliases:
            city_aliases.extend(aliases[name])
        if country in aliases:
            city_aliases.extend(aliases[country])
            
        locations.append({
            "id": f"loc_{uuid.uuid4().hex[:8]}",
            "city": name,
            "country": country,
            "display": display,
            "aliases": city_aliases
        })
        
        count += 1
        # Let's cap at 50,000 to keep memory tiny (< 10MB)
        if count > 50000:
            break

    # Add missing mandatory test cases just in case they aren't in the dataset
    mandatory = [
        {"city": "London", "country": "United Kingdom"},
        {"city": "Manchester", "country": "United Kingdom"},
        {"city": "Leeds", "country": "United Kingdom"},
        {"city": "Birmingham", "country": "United Kingdom"},
        {"city": "Glasgow", "country": "United Kingdom"},
        {"city": "Edinburgh", "country": "United Kingdom"},
        {"city": "New York", "country": "United States"},
        {"city": "Seattle", "country": "United States"},
        {"city": "Austin", "country": "United States"},
        {"city": "Boston", "country": "United States"},
        {"city": "Chicago", "country": "United States"},
        {"city": "San Francisco", "country": "United States"},
        {"city": "San Jose", "country": "United States"},
        {"city": "Los Angeles", "country": "United States"},
        {"city": "Bengaluru", "country": "India"},
        {"city": "Hyderabad", "country": "India"},
        {"city": "Pune", "country": "India"},
        {"city": "Mumbai", "country": "India"},
        {"city": "Delhi", "country": "India"},
        {"city": "New Delhi", "country": "India"},
        {"city": "Noida", "country": "India"},
        {"city": "Chennai", "country": "India"},
        {"city": "Kolkata", "country": "India"},
        {"city": "Berlin", "country": "Germany"},
        {"city": "Munich", "country": "Germany"},
        {"city": "Paris", "country": "France"},
        {"city": "Amsterdam", "country": "Netherlands"},
        {"city": "Dublin", "country": "Ireland"},
        {"city": "Barcelona", "country": "Spain"},
        {"city": "Warsaw", "country": "Poland"},
        {"city": "Stockholm", "country": "Sweden"},
        {"city": "Singapore", "country": "Singapore"},
        {"city": "Sydney", "country": "Australia"},
        {"city": "Melbourne", "country": "Australia"},
        {"city": "Toronto", "country": "Canada"},
        {"city": "Vancouver", "country": "Canada"},
        {"city": "Dubai", "country": "United Arab Emirates"},
        {"city": "Tokyo", "country": "Japan"}
    ]
    
    for m in mandatory:
        city = m["city"]
        country = m["country"]
        
        # We enforce our explicit list over random matches by inserting them at the beginning or verifying they exist.
        if not any((loc["city"] == city and loc["country"] == country) for loc in locations):
            locations.insert(0, {
                "id": f"loc_{uuid.uuid4().hex[:8]}",
                "city": city,
                "country": country,
                "display": f"{city}, {country}",
                "aliases": aliases.get(city, [])
            })
            
    os.makedirs("backend/app/data", exist_ok=True)
    with open("backend/app/data/locations.json", "w") as f:
        json.dump(locations, f)
        
    print(f"Successfully wrote {len(locations)} locations to backend/app/data/locations.json")

if __name__ == "__main__":
    generate_locations()
