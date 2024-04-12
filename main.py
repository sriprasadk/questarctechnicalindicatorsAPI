from fastapi import FastAPI, HTTPException, __version__
import yfinance as yf
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse

description = """
Try out QuestArc Technical Indicator APIs. 🚀
- Advance Decline Ratio: The Advance-Decline ratio is a technical indicator used by traders and analysts to gauge the overall health of a stock market index or individual stock. It measures the ratio of advancing stocks (those that increase in price) to declining stocks (those that decrease in price) over a given period of time.  The API calculates the ratio for the ticker based on last 6 months historic data. Also try the Quest Arc AI/ML apps to view the charts.
"""

app = FastAPI(
title="QuestArc Technical Analysis APIs",
    description=description,
   # summary="QuesttArc Technical Indicators for learning purpose. The stock prices are delayed.",
    version="0.0.1",
    contact={
        "name": "QuestArc Technical Indicators",
        "url": "https://www.questarctechnologies.com/",
     #   "email": "sales@questarctechnologies.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>Welcome to QuestArc Technical Indicator API's</title>
    </head>
    <body>
        <div class="bg-gray-200 p-4 rounded-lg shadow-lg">
            <h1>Welcome to QuestArc Technical Indicator API's version {__version__}</h1>
            <ul>
                <li><a href="/docs">/docs</a></li>
                <li><a href="/redoc">/redoc</a></li>
            </ul>
            <p>Powered by <a href="https://www.questarctechnologies.com/" target="_blank">QuestArc Technologies</a></p>
        </div>
    </body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(html)


def calculate_ad_ratio(data):
    advancers = sum(1 for close_price in data['Close'] if close_price > data['Open'][0])
    decliners = sum(1 for close_price in data['Close'] if close_price < data['Open'][0])
    ad_ratio = advancers / decliners if decliners != 0 else advancers
    return ad_ratio

@app.get("/technicalindicator/advance-decline-ratio/{ticker}")
async def get_ad_ratio(ticker: str):
    try:
        # Calculate start and end dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)  # 6 months
        
        # Download data from Yahoo Finance
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        
        if len(stock_data) == 0:
            raise HTTPException(status_code=404, detail="Stock data not found")

        # Calculate Advance-Decline Ratio
        ad_ratio = calculate_ad_ratio(stock_data)
        
        # Format the response
        response = {
            "ticker": ticker,
            "ad_ratio": ad_ratio
        }
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
