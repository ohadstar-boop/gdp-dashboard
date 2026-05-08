import streamlit as st
import yfinance as yf
import ta
import pandas as pd
from openai import OpenAI
import streamlit.components.v1 as components

# הגדרות עמוד
st.set_page_config(page_title="סורק מניות AI מתקדם", layout="wide")

# עיצוב RTL לעברית
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    div[data-testid="stSidebar"] { direction: rtl; }
    .stMetric { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def get_ai_analysis(api_key, symbol, price, rsi, action):
    """מנוע הניתוח של Grok AI"""
    if not api_key:
        return "הכנס מפתח API בתפריט הצד כדי לקבל ניתוח בינה מלאכותית."
    
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        prompt = f"נתח את מניית {symbol}. מחיר נוכחי: {price}$, מדד RSI: {round(rsi, 2)}. המלצה טכנית: {action}. כתוב סיכום קצר בעברית למשקיע לטווח קצר."
        
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "system", "content": "אתה אנליסט מניות מומחה."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"שגיאה בחיבור ל-AI: {str(e)}"

def render_chart(symbol):
    """גרף חי מ-TradingView"""
    html = f"""
    <div style="height:400px;"><script src="https://s3.tradingview.com/tv.js"></script>
    <script>new TradingView.widget({{"autosize": true, "symbol": "{symbol}", "interval": "D", "theme": "dark", "style": "1", "locale": "he_IL", "container_id": "tv_{symbol}"}});</script>
    <div id="tv_{symbol}" style="height:100%;"></div></div>
    """
    components.html(html, height=400)

def analyze_stock(symbol):
    """משיכת נתונים חיים"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1mo") # נתונים של החודש האחרון
        if data.empty: return None
        
        current_price = data['Close'].iloc[-1]
        # חישוב RSI מעודכן
        rsi_series = ta.momentum.RSIIndicator(data["Close"], window=14).rsi()
        current_rsi = rsi_series.iloc[-1]
        
        # לוגיקת המלצה
        if current_rsi < 35: action = "קנייה חזקה 🚀"
        elif current_rsi > 65: action = "מכירה/שורט 📉"
        else: action = "המתנה/נייטרלי ⚖️"
        
        return {
            "מניה": symbol,
            "מחיר": round(current_price, 2),
            "RSI": round(current_rsi, 2),
            "פעולה": action
        }
    except: return None

# --- ממשק משתמש ---
st.title("🔥 סורק מניות GOD MODE - גרסת AI")

with st.sidebar:
    st.header("הגדרות מערכת")
    api_key = st.text_input("הכנס מפתח Grok (XAI) Key:", type="password")
    watchlist_input = st.text_area("רשימת מניות (מופרדות בפסיק):", "NVDA, TSLA, AAPL, AMZN, MSFT")
    run_btn = st.button("🚀 הרץ סריקה חיה")

if run_btn:
    symbols = [s.strip().upper() for s in watchlist_input.split(",")]
    results = []
    
    with st.spinner('מושך נתונים מהבורסה ומנתח...'):
        for sym in symbols:
            res = analyze_stock(sym)
            if res: results.append(res)
    
    if results:
        # טבלת סיכום
        df = pd.DataFrame(results)
        st.subheader("📊 מצב שוק נוכחי")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # פירוט וניתוח AI
        st.divider()
        for stock in results:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader(f"ניתוח מניית {stock['מניה']}")
                st.write(f"**מחיר:** ${stock['מחיר']} | **מדד חוזק (RSI):** {stock['RSI']}")
                st.info(f"**המלצה טכנית:** {stock['פעולה']}")
                
                # הפעלת ה-AI
                if api_key:
                    with st.expander("🤖 לחץ לניתוח בינה מלאכותית (Grok)"):
                        analysis = get_ai_analysis(api_key, stock['מניה'], stock['מחיר'], stock['RSI'], stock['פעולה'])
                        st.write(analysis)
            
            with col2:
                render_chart(stock['מניה'])
            st.divider()
