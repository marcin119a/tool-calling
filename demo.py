from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

df = pd.read_csv("data/adresowo_warszawa_wroclaw.csv")

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
    
    # Sort by price (ascending) and take only first 3 records
    subset_sorted = subset.sort_values('price_total_zl_cleaned').head(3)
    return subset_sorted.to_dict(orient="records")

price_tool = StructuredTool.from_function(price_stats)
search_tool = StructuredTool.from_function(search_listings)

tools = [price_tool, search_tool]


agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

print(agent.run("Podaj statystyki cenowe dla Warszawy i Wrocławia."))
print(agent.run("Wyszukaj oferty nieruchomości dla Warszawy i maksymalnej ceny 1000000."))