import argparse
import datetime
import hmac
import requests
import random
import json
from faker import Faker
fake = Faker()

def generate_random_ticket():
    event_types = ['online_presale', 'door_sale', 'vip_ticket', 'early_bird']
    categories = ['Concert', 'Theater', 'Comedy Show', 'Art Exhibition', 'Dance Party']
    
    # Generate random price between 10 and 100
    price = round(random.uniform(10, 100), 2)
    
    # Generate random time
    hours = random.randint(18, 23)
    minutes = random.choice([0, 15, 30, 45])
    time = f"{hours:02d}:{minutes:02d}:00"
    doors = f"{hours-1:02d}:{minutes:02d}:00"

    data = {
        "event": "ticket_created",
        "details": {
            "ticket": {
                "number": f"PETZI{fake.random_number(digits=8)}",
                "type": random.choice(event_types),
                "title": fake.catch_phrase(),
                "category": random.choice(categories),
                "eventId": random.randint(1000, 9999),
                "event": fake.company(),
                "cancellationReason": "",
                "sessions": [
                    {
                        "name": f"Session at {fake.company_suffix()}",
                        "date": (datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
                        "time": time,
                        "doors": doors,
                        "location": {
                            "name": fake.company(),
                            "street": fake.street_address(),
                            "city": fake.city(),
                            "postcode": fake.postcode()
                        }
                    }
                ],
                "promoter": fake.name(),
                "price": {
                    "amount": f"{price:.2f}",
                    "currency": "CHF"
                }
            },
            "buyer": {
                "role": "customer",
                "firstName": fake.first_name(),
                "lastName": fake.last_name(),
                "postcode": fake.postcode()
            }
        }
    }
    
    return json.dumps(data)

def make_header(body, secret):
    unix_timestamp = str(datetime.datetime.timestamp(datetime.datetime.now())).split('.')[0]
    body_to_sign = f'{unix_timestamp}.{body}'.encode()
    digest = hmac.new(secret.encode(), body_to_sign, "sha256").hexdigest()
    return {
        'Petzi-Signature': f't={unix_timestamp},v1={digest}',
        'Petzi-Version': '2',
        'Content-Type': 'application/json',
        'User-Agent': 'PETZI webhook'
    }

def make_post_request(url, data, secret):
    try:
        response = requests.post(url, data=data, headers=make_header(data, secret))
        if response.status_code == 200:
            print(f"Request successful. Response: {response.text}")
        else:
            print(f"Request failed with status code {response.status_code}.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP POST Request with Random JSON Body")
    parser.add_argument("url", type=str, help="URL to send the POST request to")
    parser.add_argument("secret", nargs='?', type=str, help="secret shared between your server and petzi simulator",
                      default="secret")
    parser.add_argument("--count", type=int, help="Number of requests to send", default=1)
    args = parser.parse_args()

    for _ in range(args.count):
        data = generate_random_ticket()
        make_post_request(args.url, data, args.secret)