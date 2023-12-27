from setuptools import setup, find_packages


install_requires = [
    "aiohttp",
    "aiohttp_cors",
    "bert-serving-client",
    "faiss-cpu",
    "sqlalchemy",
    "sqlalchemy_aio",
]


setup(
    name="ChatbotAPI",
    description="Bottrick Chatbot API",
    author="Bottrick",
    author_email="feder.mato@gmail.com",
    version="1.0.0",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=["black", "flake8"],
    scripts=["scripts/bootstrap.py"],
)
