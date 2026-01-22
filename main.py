from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from core.config import settings
from presentation.scholarship.routes import router as scholarship_router
from presentation.admin.routes import router as admin_router

app = FastAPI(
    title="UMS AI Assistant",
    description="Intelligent University Assistant for Admissions, Scholarships, Masters Programs, and Registration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scholarship_router, prefix="/scholarship", tags=["Scholarship"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)