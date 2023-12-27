"""
SQUAD NOTES:
# import json
# with open(source_path) as f:
#     data = json.load(f)
# for qas in paragraph["qas"]:
#     answers = []
#     for answer in qas["answers"]:
#         answers.append(answer["text"])
#     question = qas["question"]
#     _id = qas["id"]
"""
import argparse
import asyncio
import sys
import random

from bert_serving.client import BertClient
from sqlalchemy import create_engine
from sqlalchemy.sql.ddl import CreateTable, DropTable
from sqlalchemy_aio import ASYNCIO_STRATEGY

from api.data import Qas, STATIC


def bert_session(bert_host):
    """Create bert connection"""
    return BertClient(ip=bert_host)


def db_session(db_path):
    """Create database connection"""
    return create_engine(f"sqlite:///{db_path}", strategy=ASYNCIO_STRATEGY)


QAS_SAMPLES = {
    "intents": [
        {
            "tag": "greeting",
            "patterns": [
                "Hi",
                "How are you",
                "Is anyone there?",
                "Hello",
                "Good day",
                "Whats up",
            ],
            "responses": [
                "Hello!",
                "Good to see you again!",
                "Hi there, how can I help?",
            ],
            "context_set": "",
        },
        {
            "tag": "goodbye",
            "patterns": [
                "cya",
                "See you later",
                "Goodbye",
                "I am Leaving",
                "Have a Good day",
            ],
            "responses": ["Sad to see you go :(", "Talk to you later", "Goodbye!"],
            "context_set": "",
        },
        {
            "tag": "age",
            "patterns": [
                "how old",
                "how old is Chatbot",
                "what is your age",
                "how old are you",
                "age?",
            ],
            "responses": ["I am 18 years old!", "18 years young!"],
            "context_set": "",
        },
        {
            "tag": "name",
            "patterns": [
                "what is your name",
                "what should I call you",
                "whats your name?",
            ],
            "responses": ["You can call me Chatbot.", "I'm Chatbot!"],
            "context_set": "",
        },
        {
            "tag": "shop",
            "patterns": [
                "Id like to buy something",
                "whats on the menu",
                "what do you reccommend?",
                "could i get something to eat",
            ],
            "responses": [
                "We sell chocolate chip cookies for $2!",
                "Cookies are on the menu!",
            ],
            "context_set": "",
        },
        {
            "tag": "hours",
            "patterns": [
                "when are you guys open",
                "what are your hours",
                "hours of operation",
            ],
            "responses": ["We are open 7am-4pm Monday-Friday!"],
            "context_set": "",
        },
    ]
}


async def load_dataset(bert, db):

    await db.execute(DropTable(Qas))
    await db.execute(CreateTable(Qas))

    async with db.connect() as conn:
        for item in QAS_SAMPLES["intents"]:
            title = item["tag"]

            for question in item["patterns"]:
                response = random.choice(item["responses"])
                vector = bert.encode([question])[0]
                await conn.execute(
                    Qas.insert().values(
                        static=False,
                        title=title,
                        question=question,
                        answer=response,
                        vector=";".join([str(v) for v in vector]),
                    )
                )


async def load_static(db):

    async with db.connect() as conn:

        for action, text in STATIC.items():

            await conn.execute(
                Qas.insert().values(
                    static=True,
                    question=action,
                    answer=text,
                )
            )


def main(bert_host, db_path):

    bert = bert_session(bert_host)
    db = db_session(db_path)

    asyncio.run(load_dataset(bert, db))
    asyncio.run(load_static(db))


parser = argparse.ArgumentParser(description="Bootstrap ChatBot DB")
parser.add_argument("--bert-host", default="localhost", help="BERT host address")
parser.add_argument("--db-path", default="../db/qas.sqlite", help="DB path")


if __name__ == "__main__":
    arguments = vars(parser.parse_args())
    sys.exit(main(**arguments))
