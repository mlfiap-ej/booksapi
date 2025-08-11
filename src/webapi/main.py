from .api import app

apiapp = app.get_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(apiapp, host="0.0.0.0", port=8000)
