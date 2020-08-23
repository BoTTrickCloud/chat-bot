import logging

from aiohttp import web
from sqlalchemy import select

from .data import Qas

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


bot_schema = {
    "type": "object",
    "properties": {"question": {"type": "string"}, "language": {"type": "string"},},
    "required": ["question", "language"],
    "additionalProperties": False,
}


@routes.get("/version")
async def version(request):
    return web.json_response({"version": "1.0.0"})


@routes.post("/bot")
async def bot(request, *args):
    data = await request.json()
    if data["action"]:
        return web.json_response(
            {
                "response": "action lol",
                "actions": [],
                "language": data["language"]
            }
        )

    query_vec = request.config_dict["bert"].encode([data["question"]])

    distances, idxs = request.config_dict["faiss"].search(query_vec, 1)
    async with request.config_dict["db"].connect() as conn:
        query = select([Qas.c.question, Qas.c.answer]).where(Qas.c.id == int(idxs[0][0]) + 1)
        result = await conn.execute(query)
        qas = await result.fetchall()

    distance, question, answer = round(distances[0][0]), qas[0][0], qas[0][1]

    if distance > 130:
        logger.warning(f"Distance: {distance}, ClientQ: {data['question']}, Q: {question}, A: {answer}")
        return web.json_response(
            {
                "response": "Sorry, I didn't find any valid answer. Please try to ask again or contact us by form.",
                "actions": [
                    {
                        "action": "contact_form",
                        "value": "Contact Form"
                    },
                    {
                        "action": "about_me",
                        "value": "About Me"
                    }
                ],
                "language": data["language"]
            }
        )

    logger.info(f"Distance: {distance}, ClientQ: {data['question']}, Q: {question}, A: {answer}")
    return web.json_response(
        {
            "response": answer,
            "actions": [],
            "language": data["language"]
        }
    )


@routes.get("/qas")
async def qas_get(request, *args):
    """
    pagination of QAS in DB
    """


@routes.patch("/qas")
async def qas_patch(request, *args):
    """
    Create or Update QAS to DB
    """


@routes.delete("/qas")
async def qas_delete(request, *args):
    """
    Delete QAS from DB
    """
