import logging
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from api.auth import get_api_key
from models import ChatRequest, ChatResponse
import llm

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    _=Depends(get_api_key),
) -> ChatResponse:
    logger.info(f"Received request: {request}")
    response = await llm.chat(request.model, request.messages)
    logger.info(f"Response: {response}")
    return response


class EmailCategorizeRequest(BaseModel):
    email: str
    body: str


@app.post("/api/email_categorize")
async def email_categorize(
    request: EmailCategorizeRequest,
    _=Depends(get_api_key),
):
    logger.info(f"Received request: {request}")
    response = await llm.email_categorize(request.email, request.body)
    logger.info(f"Response: {response}")
    return {"category": response}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)