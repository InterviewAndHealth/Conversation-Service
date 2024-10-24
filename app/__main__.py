import uvicorn

from app import HOST, PORT,ENV

uvicorn.run("app.main:app", host=HOST, port=PORT, reload=ENV == "development")
