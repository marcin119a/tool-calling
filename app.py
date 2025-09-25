from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import pandas as pd

# --- Setup ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# Load data
df = pd.read_csv("data/adresowo_warszawa_wroclaw.csv")

# --- Functions ---
def price_stats(city: str) -> dict:
    """Zwraca statystyki cenowe dla danego miasta."""
    subset = df[(df["city"] == city)].dropna(subset=['price_total_zl_cleaned'])
    if subset.empty:
        return {"error": f"Brak danych dla miasta {city} z czystymi cenami."}
    return {
        "mean_price": float(subset["price_total_zl_cleaned"].mean()),
        "median_price": float(subset["price_total_zl_cleaned"].median()),
        "count": int(len(subset))
    }

def search_listings(city: str, max_price: float) -> list:
    """Wyszukuje oferty nieruchomości dla danego miasta i maksymalnej ceny."""
    subset = df[(df["city"] == city) & (df["price_total_zl_cleaned"] <= max_price)].dropna(subset=['price_total_zl_cleaned'])
    if subset.empty:
        return {"error": f"Brak danych dla miasta {city} z czystymi cenami."}
    
    subset_sorted = subset.sort_values('price_total_zl_cleaned').head(3)
    return subset_sorted.to_dict(orient="records")

# Tools
price_tool = StructuredTool.from_function(price_stats)
search_tool = StructuredTool.from_function(search_listings)
tools = [price_tool, search_tool]

# Prompt
prompt = PromptTemplate(
    template="""Podaj raport dotyczący rynku nieruchomości.
    Miasto: {city}
    Limit ceny: {max_price} PLN

    1. Oblicz statystyki cenowe (średnia, mediana, liczba ogłoszeń) dla podanego miasta.
    2. Pokaż kilka mieszkań poniżej limitu ceny dla podanego miasta.
    3. Wynik sformatuj w Markdown z nagłówkami i listą punktowaną, zawierając kluczowe informacje o mieszkaniach (ulica, liczba pokoi, powierzchnia, cena).
    """,
    input_variables=["city", "max_price"]
)

agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS)

# --- FastAPI app ---
app = FastAPI(title="Real Estate API", version="1.0")

# Schemas
class ReportRequest(BaseModel):
    city: str
    max_price: float

@app.get("/price-stats/")
def get_price_stats(city: str = Query(..., description="Nazwa miasta")):
    return price_stats(city)

@app.get("/search-listings/")
def get_search_listings(
    city: str = Query(..., description="Nazwa miasta"),
    max_price: float = Query(..., description="Maksymalna cena")
):
    return search_listings(city, max_price)

@app.post("/report/")
def generate_report(request: ReportRequest):
    result = agent.run(prompt.format(city=request.city, max_price=request.max_price))
    return {"report": result}