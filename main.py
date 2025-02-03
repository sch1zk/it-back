import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.api.routes:app", host="localhost", port=8081, reload=True)