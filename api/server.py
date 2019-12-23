from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()
client = GrammarClient()


class Input(BaseModel):
    sentences: List[str]


@app.post("/fix")
def post_fix(input: Input):
    return translate(client, sentences, "model.restricted", None)
