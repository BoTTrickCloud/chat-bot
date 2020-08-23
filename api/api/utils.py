import faiss
import numpy
import logging


from .data import Qas

logger = logging.getLogger(__name__)


async def faiss_init(app):
    """Initialize Faiss index
    """
    vectors = []

    async with app["db"].connect() as conn:
        result = await conn.execute(Qas.select())
        data = await result.fetchall()

    for qas in data:
        vectors.append([float(v) for v in qas.vector.split(";")])

    array = numpy.array(vectors, dtype=numpy.float32)
    index = faiss.IndexFlatL2(len(vectors[0]))  # Build the index
    if not index.is_trained:
        raise ValueError("Faiss is not already trained")

    index.add(array)  # Add vectors to the index
    app["faiss"] = index
