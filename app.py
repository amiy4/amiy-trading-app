import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 1. Web Page Title & Layout ---
st.set_page_config(page_title="AI Live Candlestick Dashboard", layout="wide")
st.title("Amiy Kacak Personal Live Trade AI")

# Auto-updates your web app completely every 10 seconds
st_autorefresh(interval=10000, limit=None, key="datarefresh")
st.write("⏱️ *Streaming data updates live on a continuous 10-second loop.*")

# --- 2. Sidebar Configurations ---
st.sidebar.header("⚙️ Scanner Configurations")
asset_dictionary = {
    "Bitcoin (Crypto)": "BTC-USD",
    "Ethereum (Crypto)": "ETH-USD",
    "Apple Inc. (Stock)": "AAPL",
    "Tesla Inc. (Stock)": "TSLA",
    "Nvidia Corp. (Stock)": "NVDA",
    "EUR vs USD (Currency)": "EURUSD=X",
    "USD vs MYR (Currency)": "USDMYR=X"
}

selected_display_name = st.sidebar.selectbox("Choose Asset to Scan:", list(asset_dictionary.keys()))
ticker = asset_dictionary[selected_display_name]
timeframe = st.sidebar.selectbox("Choose Candlestick Interval:", ["1m", "5m", "15m", "1h", "1d"])

st.write(f"### Live Hub: **{selected_display_name}** ({timeframe} Candles)")

# --- 3. Fetch Streaming Candlestick Data Feed ---
data = yf.download(tickers=ticker, period="1d" if "m" in timeframe else "1mo", interval=timeframe)

if data.empty:
    st.error("⚠️ Data Feed Error: Unable to fetch live market prices right now.")
else:
    df = data.copy()
    
    # Flatten headings from Yahoo Finance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df.dropna()

    # --- 4. Market Math Mechanics ---
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    latest_candle = df.iloc[-1]
    live_price = float(latest_candle['Close'])
    ema_value = float(latest_candle['EMA_50'])
    
    # --- 5. Display Big Number Cards ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Live Streaming Price", f"${live_price:,.4f}" if "=X" in ticker else f"${live_price:,.2f}")
    col2.metric("Market Status", "🟢 Active Ticking")
    col3.metric("50-EMA Trend Floor", f"${ema_value:,.4f}" if "=X" in ticker else f"${ema_value:,.2f}")
    
    # --- 6. 📊 Real-Time Interactive Plotly Candlestick Chart ---
    st.write("---")
    st.subheader("📊 Zoomed Live Candlestick & Trend Chart")
    
    # Take the last 40 candlesticks for a clean, non-cluttered view
    chart_df = df.tail(40)
    
    # Build the candlestick geometry
    fig = go.Figure()
    
    # Add Candlesticks (Green for up, Red for down)
    fig.add_trace(go.Candlestick(
        x=chart_df.index,
        open=chart_df['Open'],
        high=chart_df['High'],
        low=chart_df['Low'],
        close=chart_df['Close'],
        name="Candlestick Data"
    ))
    
    # Add the 50-EMA trendline layout on top
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['EMA_50'],
        line=dict(color='#ff7f0e', width=2),
        name='50-EMA Trend Floor'
    ))
    
    # CRITICAL AUTO-ZOOM FIXED PROPERTIES:
    # 1. 'fixedrange=False' forces the Y-axis to scale perfectly around the highest/lowest candles.
    # 2. 'rangeslider_visible=False' removes the bulky bottom filter that causes layout bugs.
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=500,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(fixedrange=False)
    )
    
    # Push the beautiful candlestick chart onto your webpage app
    st.plotly_chart(fig, use_container_width=True)
    
    # --- 7. AI Logic Engine Alerts ---
    st.write("---")
    st.subheader("🤖 Live AI Assessment Output")
    
    if live_price > ema_value:
        st.success("🚨 **AI SIGNAL: BUY / UPTREND ZONE**")
        st.write("👉 **Reason:** Price candles are tracking cleanly above the 50-EMA baseline floor.")
    else:
        st.error("🚨 **AI SIGNAL: SELL / DOWNTREND WARNING**")
        st.write("👉 **Reason:** Price candles have slipped underneath the 50-EMA structural baseline floor.")