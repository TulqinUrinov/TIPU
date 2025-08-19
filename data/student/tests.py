import requests

url = "https://student.uztipi.uz/rest/v1/data/schedule-list"
token = "ns9GdRdi70s5PEHL2Esa1eqDINYcBdDP"   # senga berilgan token

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)   # studentlar ro'yxati
else:
    print("Xatolik:", response.status_code, response.text)
