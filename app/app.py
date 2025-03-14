from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID
import uvicorn
import os
from agentbuddy.agents import AgentFactory

KEYCLOAK_URL = os.environ("KEYCLOAK_URL","http://localhost:8080")
REALM = os.environ("REALM","myrealm")
CLIENT_ID = os.environ("CLIENT_ID","myclient")
REDIRECT_URI = os.environ("REDIRECT_URI","http://localhost:8000/callback")
TOKEN_URL = os.environ("TOKEN_URL",f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token")

# Configurazione Keycloak
keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                 client_id=CLIENT_ID,
                                 realm_name=REALM)

# Configura autenticazione OAuth2 con Keycloak
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/auth",
    tokenUrl=TOKEN_URL
)

# Configura FastAPI
app = FastAPI()
# templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), 'templates'))

# Funzione per verificare il token
def verify_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token not found in cookies")
    try:
        return keycloak_openid.userinfo(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# Pagina Index con login redirect
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    token = request.cookies.get("access_token")
    if token:
        try:
            user = keycloak_openid.userinfo(token)
            return templates.TemplateResponse("index.html", {"request": request, "username": user["preferred_username"]})
        except Exception as e:
            print(f"{e}")
            pass  # Se il token è scaduto, manda al login

    auth_url = (
        f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/auth"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid+profile"
    )

    return RedirectResponse(auth_url)

# Callback dopo il login
@app.get("/callback")
def callback(request: Request, code: str):
    if not code:
        return RedirectResponse("/")  # Se non c'è codice, torna alla home

    # Scambia il codice per un token
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = keycloak_openid.connection.raw_post(TOKEN_URL, data=data, headers=headers)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        response = RedirectResponse("/")
        response.set_cookie("access_token", access_token)  # Salva il token nei cookie
        return response
    
    return RedirectResponse("/")

# Endpoint protetto
@app.get("/protected")
def protected(user: dict = Depends(verify_token)):
    return {"message": f"Welcome, {user['preferred_username']}!"}

def weather_check(location: str):
    """Checking the weather for you!"""
    # Simulated weather responses
    if "sf" in location.lower() or "san francisco" in location.lower():
        return "Right now in San Francisco, it's a cool 70°F with some classic fog rolling in. Don't forget a light jacket!"
    return "It's a warm 90°F and sunny! Perfect weather to be outside—just don't forget your sunscreen."

def summarize_user_info(user_info: dict) -> str:
    """Genera una stringa riassuntiva con le informazioni salienti dell'utente."""
    summary = (
        f"Given Name: {user_info.get('given_name', 'N/A')}\n"
        f"Family Name: {user_info.get('family_name', 'N/A')}\n"
        f"Username: {user_info.get('preferred_username', 'N/A')}\n"
        f"Email: {user_info.get('email', 'N/A')} \n"
    )
    return summary

@app.post("/chat")
def chat(user: dict = Depends(verify_token), request: dict = None):
    user_message = request.get("user_message", "").strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    params = {
        "agent_id": "agent_id",
        "agent_type": "langgraph",
        "tools": [weather_check],
        "provider": "ollama",
        "model": "llama3.1:8b",
        "human": summarize_user_info(user_info=user),
    }

    agent = AgentFactory(**params)

    response = agent.interact(user_message)

    filtered_messages = response[1:]  

    if filtered_messages:
        final_message = filtered_messages[-1]
        thinking_messages = filtered_messages[:-1]
    else:
        final_message = None
        thinking_messages = []

    return {"messages": [{"text": msg.content} for msg in thinking_messages] + [{"text": final_message.content} if final_message else {}]}

@app.get("/logout")
def logout():
    response = RedirectResponse("/")
    response.delete_cookie("access_token", path="/")
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)







