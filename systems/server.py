from fastapi import FastAPI, Form, Header, File
from starlette.responses import Response
from pydantic import BaseModel
from client import GrammarClient, translate
from jinja2 import Template
from typing import List


app = FastAPI()
client = GrammarClient(8080, 5)


index_html_template = Template("""
<!DOCTYPE html>
<html>
<body>
  <p>Enter an English sentence with grammar issues</p>
  <div>
      <form action="/fix" method="post">
        <input name="sentence" size="80" autofocus></input> <input type="submit"></input>
      </form>
      {% if output_rows %}
          <table>
            <tr><td>Input</td><td>Output</td></tr>
            {% for row in output_rows %}
              <tr>
                <td>{{ row.0 }}</td>
                <td>{{ row.1 }}</td>
              </tr>
            {% endfor %}  
          </table>
      {% endif %}
  </div>
  <div>
      <form action="/upload" method="post" enctype="multipart/form-data">
        <p>Upload a text file, one line per sentence</p>
        <input type="file" name="file">
        <input type="submit">
      </form>
  </div>
</body>
</html>
""")


@app.get("/")
def index():
    return Response(content=index_html_template.render(), media_type="text/html")


@app.post("/fix")
def post_fix(sentence: str = Form(...), accept: str = Header("text/html")):
    translated = translate(client, sentence, "model.restricted", None)

    index_html = index_html_template.render(output_rows=[(sentence, translated[0])])

    accepts = [a.strip() for a in accept.split(",")]
    for a in accepts:
        mime = a.split(";")[0]
        if mime == "text/html":
            return Response(content=index_html, media_type="text/html")
        elif mime == "application/json":
            return translate(client, sentence, "model.restricted", None)


@app.post("/upload")
def upload(file: bytes = File(...)):
    sentences = [s for s in file.decode('utf-8').split('\n') if s]
    translated = translate(client, sentences, "model.restricted", None)
    return Response(content=index_html_template.render(output_rows=zip(sentences, translated),
            media_type="text/html"))
