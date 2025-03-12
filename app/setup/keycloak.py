import time
import requests
import subprocess

KEYCLOAK_URL = "http://localhost:8080"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"
REALM = "myrealm"
CLIENT_ID = "myclient"
REDIRECT_URI = "http://localhost:8000/callback"

def run_keycloak():
    print("[*] Starting Keycloak in Docker...")
    subprocess.run([
        "docker", "run", "-d", "--name", "keycloak", "-p", "8080:8080",
        "-e", "KEYCLOAK_ADMIN=admin", "-e", "KEYCLOAK_ADMIN_PASSWORD=admin",
        "quay.io/keycloak/keycloak", "start-dev"
    ])
    print("[✔] Keycloak started!")
    time.sleep(10)  # Attendi l'avvio di Keycloak

def get_admin_token():
    print("[*] Getting admin token...")
    url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": ADMIN_USER,
        "password": ADMIN_PASS
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    token = response.json()["access_token"]
    print("[✔] Got admin token!")
    return token

def create_realm(token):
    print(f"[*] Creating realm '{REALM}'...")
    url = f"{KEYCLOAK_URL}/admin/realms"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"realm": REALM, "enabled": True}
    requests.post(url, json=data, headers=headers)
    print(f"[✔] Realm '{REALM}' created!")

def create_client(token):
    print(f"[*] Creating client '{CLIENT_ID}'...")
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/clients"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "clientId": CLIENT_ID,
        "directAccessGrantsEnabled": True,
        "publicClient": True,
        "redirectUris": [REDIRECT_URI],
        "standardFlowEnabled": True,  
        "defaultClientScopes": ["profile", "email"]  
    }
    requests.post(url, json=data, headers=headers)
    print(f"[✔] Client '{CLIENT_ID}' created!")

def create_user(token):
    print("[*] Creating user 'testuser'...")
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "username": "testuser",
        "enabled": True,
        "credentials": [{"type": "password", "value": "password", "temporary": False}]
    }
    requests.post(url, json=data, headers=headers)
    print("[✔] User 'testuser' created!")

def set_token_lifetime(token_lifetime=600):
    """Imposta la durata del token di accesso a 10 minuti."""
    admin_token = get_admin_token()
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    payload = {"accessTokenLifespan": token_lifetime}  # 600 secondi = 10 minuti
    response = requests.put(url, json=payload, headers=headers)
    response.raise_for_status()
    print("✅ Token lifetime updated to 10 minutes!")
   

if __name__ == "__main__":
    run_keycloak()
    token = get_admin_token()
    create_realm(token)
    create_client(token)
    create_user(token)
    set_token_lifetime()
    print("\n🎉 Keycloak setup completed! Now start FastAPI app.\n")
