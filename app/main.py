import dotenv

dotenv.load_dotenv()

from fastapi import FastAPI

from . import dependencies, routers
from .exceptions import init_handlers

app = FastAPI()
init_handlers(app)

for dep in dependencies.__all__:
    dep = getattr(dependencies, dep)
    getattr(dep, "init_dependency", lambda: None)()

for router in routers.__all__:
    app.include_router(getattr(routers, router))
