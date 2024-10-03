import uvicorn

from app import HOST, PORT

uvicorn.run("app.main:app", host=HOST, port=PORT, reload=HOST == "localhost")
