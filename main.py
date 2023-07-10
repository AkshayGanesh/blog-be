from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.service.article import app as article
from src.service.user import app as user
from src.service.common import app as common
from src.common.logsetup import configure_logger
from src.common.settings import config

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    article,
    prefix="/api",
)
app.include_router(
    user,
    prefix="/api",
)
app.include_router(
    common,
    prefix="/api",
)


@app.on_event("startup")
async def startup_event():
    configure_logger()
        