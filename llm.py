import logging

import httpx
from models import Message, ChatResponse, ResponseMessage

logger = logging.getLogger(__name__)

LLM_ENDPOINT = "http://127.0.0.1:11434"

LLM_MODEL = "gemma3:1b"


async def email_categorize(email: str, body: str):
    system_prompt = """
    Eres un asistente que categoriza emails en una de las siguientes categorías:
    - Soporte
    - Información General
    - Ventas
    - SPAM

    Vas a responder sólo con la categoría, nada más.
    """
    messages = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=f"Email from: {email}\nBody: {body}"),
    ]

    response = await chat(LLM_MODEL, messages)
    return response.message.content


async def chat(model: str, messages: list[Message]):
    logger.info(f"Sending message to {LLM_ENDPOINT}")
    async_client = httpx.AsyncClient(timeout=120.0)
    messages_dict = [{"role": msg.role, "content": msg.content} for msg in messages]

    url = LLM_ENDPOINT + "/api/chat"
    try:
        response = await async_client.post(
            url,
            json={
                "model": model,
                "messages": messages_dict,
                "stream": False,
                "options": {
                    "num_ctx": 2048,
                },
            },
        )
        if response.status_code != 200:
            logger.error(f"Error: {response.json()}")
            raise Exception(f"Error: {response.json()}")

        response_json = response.json()
        logger.info(f"Response json: {response_json}")
        return ChatResponse(**response_json)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        if isinstance(e, TimeoutError):
            logger.error("Request timed out")
        return ChatResponse(
            model=model,
            done=True,
            message=ResponseMessage(
                role="assistant",
                content="Oops, ocurrió un error. Por favor, intenta de nuevo.",
            ),
        )