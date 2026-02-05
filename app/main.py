
from fastapi import FastAPI
from .core.config import settings
from .database.mongo import init_indexes
from .routers import auth, customer, manager, verification, admin, transactions

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
async def on_startup():
    await init_indexes()

app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(customer.router, prefix=settings.API_PREFIX)
app.include_router(manager.router, prefix=settings.API_PREFIX)
app.include_router(verification.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)
app.include_router(transactions.router, prefix=settings.API_PREFIX)

@app.get('/')
async def health():
    return {"status": "ok"}
