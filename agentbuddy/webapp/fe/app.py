import uvicorn

if __name__ == "__main__":
    uvicorn.run("agentbuddy.webapp.fe.api:app", host="0.0.0.0", port=8001, workers=4)