from fastapi import FastAPI

from . import routers
from .exceptions import init_handlers

app = FastAPI()
init_handlers(app)

for router in routers.__all__:
    app.include_router(getattr(routers, router))
