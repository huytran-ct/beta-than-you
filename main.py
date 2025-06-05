from fastapi import FastAPI
from router.ad_info import router as ad_info_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from agent-test!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include the ad_info router
app.include_router(ad_info_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
