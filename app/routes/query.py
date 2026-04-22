
from fastapi import APIRouter
from app.routes.upload import DATA_STORE
from app.services.llm_service import ask_llm
import traceback
import pandas as pd
import json
router = APIRouter()

import re

from pydantic import BaseModel

class AskRequest(BaseModel):
    session_id: str
    question: str

def clean_code(code: str) -> str:
    # Remove triple backtick blocks (```python ... ```)
    code = re.sub(r"```[a-zA-Z]*\n?", "", code)
    code = code.replace("```", "")

    return code.strip()

def normalize_step(step):
    if step["aggregation"] == "count" and not step.get("y"):
        step["aggregation"] = "size"
    return step

def run_step(df, step):
    step = normalize_step(step)
    print('begin running step', step)
    agg = step["aggregation"]
    groupby = step["groupby"]
    y = step["y"]

    if step["aggregation"] == "count":
        if step.get("y") is None:
            step["aggregation"] = "size"

    if step["aggregation"] == "sum":
        assert step.get("y") is not None

    if step["groupby"] and not step.get("x"):
        step["x"] = step["groupby"]

    if groupby:
        grouped = df.groupby(groupby)[y]

        if agg == "sum":
            result = grouped.sum().reset_index()
        elif agg == "avg":
            result = grouped.mean().reset_index()
        elif agg == "count":
            result = grouped.count().reset_index()
    else:
        if agg == "sum":
            result = df[y].sum()
        elif agg == "avg":
            result = df[y].mean()
        elif agg == "count":
            result = df[y].count()

    return result

import matplotlib.pyplot as plt
import uuid

def generate_chart(data, step):
    chart_id = str(uuid.uuid4()) + ".png"
    path = f"static/{chart_id}"

    fig, ax = plt.subplots()

    if step["type"] == "bar":
        data.plot(kind="bar", x=step["x"], y=step["y"], ax=ax)

    elif step["type"] == "line":
        data.plot(kind="line", x=step["x"], y=step["y"], ax=ax)

    plt.title(step["title"])
    plt.savefig(path)
    plt.close()

    return path



@router.post("/ask")
async def query_data(req: AskRequest):
    session_id = req.session_id
    question = req.question
    df = DATA_STORE.get(session_id)
    # df.info()
    prompt = f"""
        You are a senior data analyst.

        Given a dataframe df with columns:
        {list(df.columns)}

        User question:
        {question}

        Return a JSON list of analysis steps.

        Each step must follow this format:
        [
        {{
            "title": "Chart title",
            "type": "bar | line | table | metric",
            "x": "column",
            "y": "column",
            "aggregation": "sum | avg | count",
            "groupby": "column or null",
            "insight": "short explanation"
        }}
        ]

        Rules:
        - No python code
        - No markdown
        - Only JSON
        - Max 4 steps
        """

    plan_json = ask_llm(prompt)
    steps = json.loads(plan_json)
    print('steps', steps)
    results = []
    img_charts = []

    for step in steps:
        data = run_step(df, step)

        item = {
            "title": step["title"],
            "insight": step["insight"],
            "type": step["type"]
        }

        if step["type"] in ["bar", "line"]:
            chart_path = generate_chart(data, step)
            item["chart"] = chart_path
            img_charts.append(chart_path)

        elif step["type"] == "table":
            item["table"] = data.to_dict()

        else:
            item["value"] = str(data)

        results.append(item)

    # return {"dashboard": results}
    return {
        "answer": "",
        "charts": img_charts
    }
