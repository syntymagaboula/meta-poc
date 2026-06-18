from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def home():
    return {"status": "META-POC running"}

@app.get("/webhook-test")
def test():
    return {"status": "ok"}

@app.post("/webhook/facebook")
async def fb(request: Request):
    data = await request.json()
    print("MESSAGE FACEBOOK:", data)
    return {"received": True}
