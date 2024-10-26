import uvicorn

from app import ENV, HOST, PORT

uvicorn.run("app.main:app", host=HOST, port=PORT, reload=ENV == "development")
