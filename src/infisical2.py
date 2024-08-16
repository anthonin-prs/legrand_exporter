from infisical_client import *
import json


base_infisical_domain = "https://infisical.ebe.ovh"


client = InfisicalClient(ClientSettings(
    auth=AuthenticationOptions(
        universal_auth=UniversalAuthMethod(
            client_id="9b4404ab-6344-4d13-adc0-a8764458e45f",
            client_secret="6eecceb1f54cd43ac6b39bea9edc664e5696603949f89a89e4f7c2f0e4545693",
        )
    ),
    site_url=base_infisical_domain
))

secret = client.getSecret(options=GetSecretOptions(
    environment="vps",
    project_id="fe247bba-4b37-43d7-8e29-030cf758ede3",
    path="/Supervision/Netatmo",
    secret_name="CLIENT_ID"
))

print(secret.secret_value)

secret2 = client.updateSecret(options=UpdateSecretOptions(
    environment="vps",
    project_id="fe247bba-4b37-43d7-8e29-030cf758ede3",
    path="/Supervision/Netatmo",
    secret_name="CLIENT_ID",
    secret_value="6668a022c9fc99621e0e9e66",
))

print(secret2)

secret = client.getSecret(options=GetSecretOptions(
    environment="vps",
    project_id="fe247bba-4b37-43d7-8e29-030cf758ede3",
    path="/Supervision/Netatmo",
    secret_name="CLIENT_ID"
))
print(secret.secret_value)
