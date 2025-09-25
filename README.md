# Real Estate API

FastAPI application for real estate data analysis and search.

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the API

Start the FastAPI server with auto-reload:
```bash
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /cities` - Get available cities
- `POST /price-stats` - Get price statistics for a city
- `POST /search-listings` - Search for real estate listings

## Example Usage

### Get price statistics:
```bash
curl -X POST "http://localhost:8000/price-stats" \
     -H "Content-Type: application/json" \
     -d '{"city": "Warszawa"}'
```

### Search listings:
```bash
curl -X POST "http://localhost:8000/search-listings" \
     -H "Content-Type: application/json" \
     -d '{"city": "Warszawa", "max_price": 300000}'
```

