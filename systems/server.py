from fastapi import FastAPI
from pydantic import BaseModel
from client import GrammarClient
from typing import List


app = FastAPI()
client = GrammarClient(8080, 4000)


class Input(BaseModel):
    sentences: List[str]


@app.post("/fix")
def post_fix(input: Input):
    return translate(client, sentences, "model.restricted", None)
