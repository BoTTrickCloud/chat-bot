from sqlalchemy import Column, Integer, String, MetaData, Table, Boolean

metadata = MetaData()


Qas = Table(
    'qas', metadata,
    Column("id", Integer, primary_key=True),
    Column("static", Boolean),
    Column("qas_id", Integer),
    Column("title", String),
    Column("question", String),
    Column("answer", String),
    Column("vector", String),

)


STATIC = {
    "about_me": "A chatbot is an artificial intelligence (AI) software that can simulate a conversation (or a chat) with a user in natural language through messaging application,",
}
