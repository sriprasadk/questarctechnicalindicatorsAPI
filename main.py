from fastapi import FastAPI, HTTPException, __version__, WebSocket
import yfinance as yf
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse
import json

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

#@app.get("/")
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

    
@app.get("/technicalindicator/advance-decline-ratio/{ticker}", tags=["Advance Decline Ratio"])
async def get_Advance_Decline_ratio(ticker: str):
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

@app.get("/technicalindicator/relative-strength-index/{ticker}", tags=["Relative Strength Index"])
async def get_Relative_Strength_Index(ticker: str):
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
    

def calculate_vortex(data, window=14):
    high = data['High']
    low = data['Low']
    close = data['Close']
    
    tr = abs(high - low.shift(1)).rolling(window=window).sum()
    vm = abs(low - close.shift(1)).rolling(window=window).sum()
    vp = abs(high - close.shift(1)).rolling(window=window).sum()
    
    vi_plus = vm / tr
    vi_minus = vp / tr
    
    return vi_plus, vi_minus
    
@app.get("/technicalindicator/VortexIndicator/{ticker}", tags=["Vortex Indciator"])
async def get_Vortex_Indicator(ticker: str):
    try:
        # Fetch data from Yahoo Finance
        print("Ticker", ticker)
        df = yf.download(ticker, period="1y")
        print(df)
        # Check if data is available
        if df.empty:
            raise HTTPException(status_code=404, detail="No data available for this ticker.")

        vi_plus, vi_minus = calculate_vortex(df)
        latest_vi_plus = vi_plus.iloc[-1]
        latest_vi_minus = vi_minus.iloc[-1]
       # await websocket.send_text(json.dumps({"Vortex_Indicator_Plus": latest_vi_plus, "Vortex_Indicator_Minus": latest_vi_minus}))

        return {"ticker": ticker, "Vortex_Indicator_Plus": latest_vi_plus,"Vortex_Indicator_Minus": latest_vi_minus}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/vortex")
async def vortex(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            ticker = data['ticker']
            calculate_indicator = data.get('calculate_indicator', False)
            
            # Fetch data from Yahoo Finance
            df = yf.download(ticker, period="1y")
            
            if df.empty:
                await websocket.send_text(json.dumps({"error": "No data available for this ticker."}))
            else:
                if calculate_indicator:
                    vi_plus, vi_minus = calculate_vortex(df)
                    latest_vi_plus = vi_plus.iloc[-1]
                    latest_vi_minus = vi_minus.iloc[-1]
                    await websocket.send_text(json.dumps({"Vortex_Indicator_Plus": latest_vi_plus, "Vortex_Indicator_Minus": latest_vi_minus}))
                else:
                    await websocket.send_text(json.dumps({"Vortex_Indicator_Plus": "Not calculated", "Vortex_Indicator_Minus": "Not calculated"}))
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))

@app.get("/",tags=["Vortex Indciator WebSocket API"])
async def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vortex Indicator Calculator</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center mb-4">QuestArc Technical Indicators</h1>
            <h2 class="text-center mb-4">WebSocket API </h2>
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <form id="calcForm">
                        <div class="form-group">
                            <label for="ticker">Enter Ticker Symbol:</label>
                            <input type="text" class="form-control" id="ticker" name="ticker">
                        </div>
                        <div class="form-group form-check">
                            <input type="checkbox" class="form-check-input" id="calculateIndicator" name="calculateIndicator">
                            <label class="form-check-label" for="calculateIndicator">Calculate Vortex Indicator</label>
                        </div>
                        <button type="submit" class="btn btn-primary">Submit</button>
                    </form>
                </div>
            </div>

            <div class="row justify-content-center mt-4">
                <div class="col-md-6">
                    <div id="result" class="alert alert-info" role="alert" style="display: none;"></div>
                </div>
            </div>
            
            <h2 class="text-center mb-4">REST APIs</h1>
            <div>
                   <center> <a href="/docs"><h3>/docs</h3></a>
                    <a href="/redoc"><h3>/redoc</h3></a>
                    </center>
                
            <div>    
        </div>
        
        <footer class="footer mt-5">
        <div class="container text-center">
            <span class="text-muted">Powered by <a href="https://www.questarctechnologies.com">QuestarcTechnologies</a> | Contact: <a href="mailto:sales@questarctechnologies.com">sales@questarctechnologies.com</a></span>
        </div>
    </footer>
        
        <script>
            const form = document.getElementById('calcForm');
            form.addEventListener('submit', async (event) => {
                event.preventDefault();
                
                const ticker = document.getElementById('ticker').value;
                const calculateIndicator = document.getElementById('calculateIndicator').checked;

                const ws = new WebSocket('ws://localhost:8000/vortex');
                ws.onopen = () => {
                    const data = JSON.stringify({ticker: ticker, calculate_indicator: calculateIndicator});
                    ws.send(data);
                };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    console.log(data);
                    // Handle response data here, for example, display it on the page
                    const resultElement = document.getElementById('result');
                    resultElement.style.display = 'block';
                    resultElement.innerHTML = `<strong>Vortex Indicator Plus:</strong> ${data.Vortex_Indicator_Plus}, <strong>Vortex Indicator Minus:</strong> ${data.Vortex_Indicator_Minus}`;
                };

                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
