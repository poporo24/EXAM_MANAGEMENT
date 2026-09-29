import requests
import json

API_KEY = "AIzaSyCjf-aMcch8I9thXy5Lw1QzWfUX3sOAwhE"
url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

data = {
    "email": "jpbaltazar23-0368@cca.edu.ph",
    "password": "SuperAdmin@2024",
    "returnSecureToken": True
}

resp = requests.post(url, json=data)
print(resp.status_code)
print(json.dumps(resp.json(), indent=2))
