from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Union
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Load the data
df = pd.read_csv("data/adresowo_warszawa_wroclaw.csv")

app = FastAPI(
    title="Real Estate API",
    description="API for real estate data analysis and search",
    version="1.0.0"
)

# Pydantic models for request/response
class PriceStatsRequest(BaseModel):
    city: str

class PriceStatsResponse(BaseModel):
    mean_price: float
    median_price: float
    count: int

class PriceStatsErrorResponse(BaseModel):
    error: str

class SearchListingsRequest(BaseModel):
    city: str
    max_price: float

class ListingItem(BaseModel):
    # Define the structure based on your CSV columns
    # You may need to adjust these fields based on your actual data structure
    street: str = None
    rooms: int = None
    area: float = None
    price_total_zl_cleaned: float = None
    city: str = None

class SearchListingsResponse(BaseModel):
    listings: List[Dict[str, Any]]

class SearchListingsErrorResponse(BaseModel):
    error: str

@app.get("/")
async def root():
    return {"message": "Real Estate API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/price-stats", response_model=Union[PriceStatsResponse, PriceStatsErrorResponse])
async def get_price_stats(request: PriceStatsRequest):
    """
    Get price statistics for a given city.
    """
    try:
        subset = df[(df["city"] == request.city)].dropna(subset=['price_total_zl_cleaned'])
        if subset.empty:
            return PriceStatsErrorResponse(error=f"Brak danych dla miasta {request.city} z czystymi cenami.")
        
        return PriceStatsResponse(
            mean_price=float(subset["price_total_zl_cleaned"].mean()),
            median_price=float(subset["price_total_zl_cleaned"].median()),
            count=int(len(subset))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-listings", response_model=Union[SearchListingsResponse, SearchListingsErrorResponse])
async def search_listings(request: SearchListingsRequest):
    """
    Search for real estate listings in a city below a maximum price.
    """
    try:
        subset = df[(df["city"] == request.city) & (df["price_total_zl_cleaned"] <= request.max_price)].dropna(subset=['price_total_zl_cleaned'])
        if subset.empty:
            return SearchListingsErrorResponse(error=f"Brak danych dla miasta {request.city} z czystymi cenami.")
        
        # Sort by price (ascending) and take only first 3 records
        subset_sorted = subset.sort_values('price_total_zl_cleaned').head(3)
        listings = subset_sorted.to_dict(orient="records")
        
        return SearchListingsResponse(listings=listings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cities")
async def get_available_cities():
    """
    Get list of available cities in the dataset.
    """
    try:
        cities = df['city'].unique().tolist()
        return {"cities": cities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
