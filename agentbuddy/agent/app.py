from .api_v1 import app, port
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(port), workers=1)
