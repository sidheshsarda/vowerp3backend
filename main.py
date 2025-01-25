from fastapi import FastAPI
import logging



# Import routes
from inventory.routes import router as inventory_router
from hrms.routes import router as hrms_router
from accounts.routes import router as accounts_router
from authorization.routes import router as authorization_router
from doffing.routes import router as doffing_router
from master.routes import router as master_router

# Initialize FastAPI app
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your React app's URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Include routers
app.include_router(accounts_router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(inventory_router, prefix="/api/inventoryRoute", tags=["Inventory"])
app.include_router(hrms_router, prefix="/api/hrms", tags=["HRMS"])
#app.include_router(authorization_router, prefix="/api/authRoutes", tags=["Authorization"])
app.include_router(authorization_router, prefix="/api/authRoutes", tags=["Authorization"])
app.include_router(doffing_router, prefix="/api/doffRoutes", tags=["Doffing"])
app.include_router(master_router, prefix="/api/masterRoutes", tags=["Master"])



# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application is shutting down...")

if __name__ == "__main__":
    import uvicorn
    try:
        logger.info("Starting server on http://0.0.0.0:5004")
        uvicorn.run("main:app", host="0.0.0.0", port=5004)
    except Exception as e:
        logger.error(f"Failed to start the server: {e}")
