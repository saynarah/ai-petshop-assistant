import logging
from fastapi import FastAPI
from ai_petshop_assistant.controllers.message_controller import router as message_router
from ai_petshop_assistant.controllers.whatsapp_controller import router as whatsapp_router
from ai_petshop_assistant.controllers.document_controller import router as document_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI Pet Shop Assistant",
    description="AI-powered customer support for pet shops",
    version="0.1.0"
)

## register routers
app.include_router(message_router)
app.include_router(whatsapp_router)
app.include_router(document_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}