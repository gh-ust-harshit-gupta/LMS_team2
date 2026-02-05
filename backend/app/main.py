from fastapi import FastAPI
from app.controllers.auth_controller import router as auth_router
from app.controllers.kyc_controller import router as kyc_router
from app.controllers.verification_controller import router as verification_router

app = FastAPI(title="Loan Management System")

app.include_router(auth_router)
app.include_router(kyc_router)
app.include_router(verification_router)