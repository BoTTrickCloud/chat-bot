import logging

import sqlalchemy as sql
from aiohttp import web

from .data import Qas
from .utils import faiss_add, faiss_remove, faiss_update

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
        async with request.config_dict["db"].connect() as conn:
            result = await conn.execute(sql.select(
                [Qas.c.answer]
            ).where(
                sql.and_(
                    (Qas.c.static.is_(True)),
                    (Qas.c.question == data["question"])
                )
            ))
            qas = await result.fetchone()
        return web.json_response(
            {
                "response": qas.answer,
                "actions": [],
                "language": data["language"]
            }
        )

    query_vec = request.config_dict["bert"].encode([data["question"]])

    distances, idxs = request.config_dict["faiss"].search(query_vec, 1)
    async with request.config_dict["db"].connect() as conn:
        result = await conn.execute(sql.select(
            [Qas.c.question, Qas.c.answer]
        ).where(
            sql.and_(
                (Qas.c.static.is_(False)),
                (Qas.c.id == int(idxs[0][0])))
            )
        )
        qas = await result.fetchone()

    distance, question, answer = round(distances[0][0]), qas.question, qas.answer

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
    Get list of QAS from DB, TODO: pagination
    """
    columns = [Qas.c.id, Qas.c.question, Qas.c.answer]

    async with request.config_dict["db"].connect() as conn:
        data_res = await conn.execute(sql.select(columns).where(Qas.c.static.is_(False)))
        data = await data_res.fetchall()

    column_names = [column.name for column in columns]
    qas = [dict(zip(column_names, row)) for row in data]
    return web.json_response(qas)


@routes.put("/qas")
async def qas_put(request, *args):
    """
    Add QAS to DB
    """
    data = await request.post()

    query_vec = request.config_dict["bert"].encode([data["question"]])[0]
    vector = ";".join([str(v) for v in query_vec])
    qas = {
        "static": False,
        "question": data["question"],
        "answer": data["answer"],
        "vector": vector
    }
    async with request.config_dict["db"].connect() as conn:
        await conn.execute(Qas.insert().values(qas))
        id_res = await conn.execute(sql.select([Qas.c.id]).where(Qas.c.vector == vector))
        _id = await id_res.fetchone()

    faiss_add(request.config_dict["faiss"], _id[0], query_vec)

    qas.update({"id": _id[0]})
    qas.pop("vector")
    qas.pop("static")
    return web.json_response(qas)


@routes.delete("/qas")
async def qas_delete(request, *args):
    """
    Delete QAS from DB
    """
    data = await request.post()

    qas = {
        "id": data["id"],
        "question": data["question"],
        "answer": data["answer"],
    }
    async with request.config_dict["db"].connect() as conn:
        await conn.execute(Qas.delete().where(Qas.c.id == data["id"]))

    faiss_remove(request.config_dict["faiss"], data["id"])

    return web.json_response(qas)


@routes.post("/qas")
async def qas_post(request, *args):
    """
    Edit QAS in DB
    """
    data = await request.post()

    query_vec = request.config_dict["bert"].encode([data["question"]])[0]
    vector = ";".join([str(v) for v in query_vec])
    qas = {
        "static": False,
        "question": data["question"],
        "answer": data["answer"],
        "vector": vector
    }
    async with request.config_dict["db"].connect() as conn:
        await conn.execute(Qas.update().values(qas).where(Qas.c.id == data["id"]))

    faiss_update(request.config_dict["faiss"], data["id"], query_vec)

    qas.update({"id": data["id"]})
    qas.pop("vector")
    qas.pop("static")
    return web.json_response(qas)
