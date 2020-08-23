import argparse
import asyncio
import json
import sys

from bert_serving.client import BertClient
from sqlalchemy import create_engine
from sqlalchemy.sql.ddl import CreateTable, DropTable
from sqlalchemy_aio import ASYNCIO_STRATEGY

from api.data import Qas, STATIC


def bert_session(bert_host):
    """Create bert connection
    """
    return BertClient(ip=bert_host)


def db_session(db_path):
    """Create database connection
    """
    return create_engine(f"sqlite:///{db_path}", strategy=ASYNCIO_STRATEGY)


async def load_dataset(bert, db, source_path):

    with open(source_path) as f:
        data = json.load(f)

    # await db.execute(DropTable(Qas))
    await db.execute(CreateTable(Qas))

    async with db.connect() as conn:
        for item in data["data"]:
            title = item["title"]
            for paragraph in item["paragraphs"]:
                for qas in paragraph["qas"]:
                    answers = []
                    for answer in qas["answers"]:
                        answers.append(answer["text"])
                    question = qas["question"]
                    _id = qas["id"]
                    vector = bert.encode([question])[0]
                    await conn.execute(Qas.insert().values(
                        static=False,
                        qas_id=_id,
                        title=title,
                        question=question,
                        answer=answers[0],
                        vector=";".join([str(v) for v in vector])
                    ))


async def load_static(db):

    async with db.connect() as conn:

        for action, text in STATIC.items():

            await conn.execute(Qas.insert().values(
                static=True,
                question=action,
                answer=text,
            ))


def main(bert_host, db_path, source_path, static):

    bert = bert_session(bert_host)
    db = db_session(db_path)

    if not static:
        asyncio.run(load_dataset(bert, db, source_path))
    else:
        asyncio.run(load_static(db))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstrap ChatBot DB")
    parser.add_argument(
        "--bert-host",
        default="localhost",
        help="BERT host address"
    )
    parser.add_argument(
        "--db-path",
        default="../../data/db/qas.sqlite",
        help="DB path"
    )
    parser.add_argument(
        "--source-path",
        default="../../data/dev-v1.1.json",
        help="Source file path"
    )
    parser.add_argument(
        "--static",
        help="Enable the static load.",
        action="store_true",
    )
    arguments = vars(parser.parse_args())
    sys.exit(main(**arguments))
