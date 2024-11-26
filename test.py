import requests
api_url = "https://1xpanel.com/api/v2"
api_key = "6b1bea025185a663cb0a3b08b6526a60"

params = {'key': api_key, 'action': 'cancel','orders':14161221}

response = requests.get(api_url,params)


if response.status_code == 200:
    print(response.json())





















