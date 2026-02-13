import io
import os
import sys
import json
import tempfile
from pathlib import Path

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

# ================= DATA LOADER =================
def load_data(file_or_path):
    if isinstance(file_or_path, (str, Path)):
        ext = Path(file_or_path).suffix.lower()
        if ext == ".csv":
            return pd.read_csv(file_or_path)
        if ext in [".xls", ".xlsx"]:
            return pd.read_excel(file_or_path)

    raw = file_or_path.read()
    return pd.read_csv(io.BytesIO(raw))


# ================= SUGGESTION PROMPTS =================
def suggest_prompts(df: pd.DataFrame):
    """
    Advanced Business Intelligence Prompts
    """

    prompts = [

        # BASIC OVERVIEW
        "Show total revenue generated in the dataset.",
        "Show overall total quantity sold.",
        "Display dataset summary with business insights.",

        # CATEGORY ANALYSIS
        "Show category-wise total revenue and percentage contribution.",
        "Create a pie chart of revenue distribution by category.",
        "Create a bar chart of category-wise total sales.",
        "Identify highest revenue generating category.",

        # PRODUCT PERFORMANCE
        "Show top 10 best selling products based on quantity.",
        "Show top 10 highest revenue generating products.",
        "Show bottom 5 least selling products.",
        "Identify slow moving products based on low sales volume.",

        # PROFIT ANALYSIS
        "Calculate total profit if cost price and selling price columns exist.",
        "Show profit percentage per product.",
        "Identify products with lowest profit margin.",
        "Find products generating highest profit margin.",

        # INVENTORY INSIGHTS
        "Identify low stock products that require restocking.",
        "Show products with high stock but low sales.",
        "Highlight dead stock items with zero sales.",

        # TREND ANALYSIS
        "Show monthly sales trend using a line chart.",
        "Identify seasonal sales pattern from date column if available."
    ]

    return prompts


# ================= CODE EXECUTOR =================
def run_code(df, code):
    local_vars = {"df": df, "pd": pd, "np": np, "plt": plt}
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    try:
        exec(code, {}, local_vars)

        if plt.get_fignums():
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                plt.savefig(f.name, bbox_inches="tight")
                plt.close("all")
                return {"type": "image", "path": f.name}

        if "result" in local_vars:
            res = local_vars["result"]
            if isinstance(res, pd.DataFrame):
                return {"type": "dataframe", "df": res}
            return {"type": "text", "output": str(res)}

        return {"type": "text", "output": buffer.getvalue()}

    except Exception as e:
        return {"type": "text", "output": str(e)}

    finally:
        sys.stdout = old_stdout


# ================= OPENROUTER API =================
def ask_llm(prompt: str):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return "OPENROUTER_API_KEY missing"

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "stepfun/step-3.5-flash:free",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a data analyst. "
                        "Return ONLY python code inside ```python``` blocks. "
                        "DataFrame name is df."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        })
    )

    return response.json()["choices"][0]["message"]["content"]

