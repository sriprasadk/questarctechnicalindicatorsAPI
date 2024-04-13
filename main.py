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
    open_price = data['Open'][0]  # Get the open price of the first day
    
    # Count the number of advancers and decliners
    advancers = sum(1 for close_price in data['Close'] if close_price > open_price)
    decliners = sum(1 for close_price in data['Close'] if close_price < open_price)
    
    # Calculate the Advance-Decline ratio
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


def calculate_rsi(data, window=14):
    delta = data.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@app.get("/technicalindicator/relative-strength-index/{ticker}")
async def get_rsi(ticker: str):
    try:
        # Fetch data from Yahoo Finance
        end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
        df = yf.download(ticker, start=start_date, end=end_date)

        # Check if data is available
        if df.empty:
            raise HTTPException(status_code=404, detail="No data available for this ticker.")

        # Calculate RSI
        df['RSI'] = calculate_rsi(df['Close'])

        # Get the latest RSI value
        latest_rsi = df['RSI'].iloc[-1]

        return {"ticker": ticker, "Relative Strength Index": latest_rsi}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))