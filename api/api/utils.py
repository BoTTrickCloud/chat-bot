import faiss
import numpy
import logging

from sqlalchemy import select

from .data import Qas

logger = logging.getLogger(__name__)


async def faiss_init(app):
    """Initialize Faiss index
    """
    ids = []
    vectors = []

    async with app["db"].connect() as conn:
        result = await conn.execute(select([Qas.c.id, Qas.c.vector]).where(Qas.c.static == 0))
        data = await result.fetchall()

    for qas in data:
        ids.append(qas.id)
        vectors.append([float(v) for v in qas.vector.split(";")])

    vectors_array = numpy.array(vectors, dtype=numpy.float32)
    ids_array = numpy.array(ids)

    index = faiss.IndexFlatL2(vectors_array.shape[1])  # Build the index (size 768)
    index_map = faiss.IndexIDMap(index)

    if not index.is_trained:
        raise ValueError("Faiss is not already trained")

    index_map.add_with_ids(vectors_array, ids_array)  # Add vectors to the index
    # index.add(array)
    app["faiss"] = index_map


def faiss_add(index, _id, vector):
    """Add Faiss index
    """
    vector_array = numpy.array([vector], dtype=numpy.float32)
    id_array = numpy.array([int(_id)])
    index.add_with_ids(vector_array, id_array)  # Add vector to the index


def faiss_remove(index, _id):
    """Remove Faiss index
    """
    index.remove_ids(numpy.array([int(_id)]))


def faiss_update(index, _id, vector):
    """Update Faiss index
    """
    faiss_remove(index, _id)
    faiss_add(index, _id, vector)
