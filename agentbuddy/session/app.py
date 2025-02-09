import uvicorn

if __name__ == "__main__":
    uvicorn.run("agentbuddy.session.api_v1:app", host="0.0.0.0", port=8002, workers=1)
