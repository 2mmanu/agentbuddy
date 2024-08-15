from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
import os

try:
    import agentbuddy
    path = os.path.dirname(agentbuddy.__file__)
except Exception as e:
    print(f"ops! using local dir: {e}")
    path = "./agentbuddy"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(path,"webapp/fe/static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def get():
    async with aiofiles.open(os.path.join(path,"webapp/fe/static/chat.html"), mode="r") as file:
        content = await file.read()
    return HTMLResponse(content=content)

# Avvio dell'app con uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
