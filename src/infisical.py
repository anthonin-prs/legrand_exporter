import requests
import urllib3
import json

urllib3.disable_warnings()

base__infisical_domain = "https://infisical.ebe.ovh"

payload = {
    "clientId": "9b4404ab-6344-4d13-adc0-a8764458e45f",
    "clientSecret": "6eecceb1f54cd43ac6b39bea9edc664e5696603949f89a89e4f7c2f0e4545693"
}
headers = {"Content-Type": "application/json"}

response = requests.request("POST", base__infisical_domain +
                            "/api/v1/auth/universal-auth/login", json=payload, headers=headers).json()

if 'error' in response:
    print("Can't login", response)
    exit(1)
else:
    token = response['accessToken']


headers = {"Content-Type": "application/json",
           "Authorization": "Bearer "+token}

querystring = {"workspaceId": "fe247bba-4b37-43d7-8e29-030cf758ede3",
               "environment": "vps",
               "secretPath": "/Supervision/Netatmo"}

response = requests.request(
    "GET", base__infisical_domain+"/api/v3/secrets/raw/CLIENT_ID", headers=headers, params=querystring)


print(response.text)

payload = {
    "workspaceId": "fe247bba-4b37-43d7-8e29-030cf758ede3",
    "environment": "vps",
    "secretValue": "6668a022c9fc99621e0e9e66",
    "secretPath": "/Supervision/Netatmo"
}

response = requests.request("PATCH", base__infisical_domain +
                            "/api/v3/secrets/raw/CLIENT_ID", json=payload, headers=headers)
print(response.text)


response = requests.request(
    "GET", base__infisical_domain+"/api/v3/secrets/raw/CLIENT_ID", headers=headers, params=querystring)
print(response.text)
