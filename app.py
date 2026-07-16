import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from textblob import TextBlob

# ==========================================
# إعدادات الصفحة وهوية التطبيق (branding)
# ==========================================
st.set_page_config(
    page_title="مستشار الاستثمار الذكي - مصرف الإنماء",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #002D62; text-align: center; margin-bottom: 20px; }
    .stButton>button { background-color: #002D62; color: white; width: 100%; border-radius: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #D4AF37; color: #002D62; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='main-title'>منصة مستشار الاستثمار الذكي (حصري لعملاء مصرف الإنماء)</div>",
    unsafe_allow_html=True,
)
st.write(
    "أداة مدعومة بالذكاء الاصطناعي التفسيري (XAI) لتحليل الأسهم، الأخبار الحية، ومشاعر المستثمرين لدعم اتخاذ القرار المالي."
)
st.write("---")

# ==========================================
# لوحة التحكم الجانبية (Sidebar)
# ==========================================
st.sidebar.header("إعدادات التحليل الذكي")

stock_options = {
    "مصرف الإنماء (1150)": {"ticker": "1150.SR", "backup_price": 24.83, "backup_news": "Alinma Bank reports record breaking net profit growth this quarter with expanding digital banking services."},
    "أرامكو السعودية (2222)": {"ticker": "2222.SR", "backup_price": 30.10, "backup_news": "Saudi Aramco expands its global energy supply chains and strengthens sustainable investment initiatives."},
    "مصرف الراجحي (1120)": {"ticker": "1120.SR", "backup_price": 85.50, "backup_news": "Al Rajhi Bank premium banking segments witness increased customer onboarding due to upgraded app features."},
}

selected_stock_label = st.sidebar.selectbox("اختر السهم:", list(stock_options.keys()))
stock_info = stock_options[selected_stock_label]

st.sidebar.info("تنبيه: النظام الآن يسحب السعر وآخر الأخبار تلقائياً من الإنترنت بمجرد الضغط على الزر بالأسفل.")

run_analysis = st.sidebar.button("ابدأ التحليل الفوري وربط البيانات الحية")


# ==========================================
# دالة جلب البيانات الحية (الأسعار + الأخبار) من الإنترنت
# ==========================================
def get_live_market_and_news(ticker_symbol, info_dict):
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # 1. سحب السعر الحي وبيانات السوق لآخر 5 أيام لمعرفة حركة السهم
        df = stock.history(period="5d")
        if df.empty or len(df) < 2:
            raise Exception("خطأ اتصال")
        live_price = stock.info.get("currentPrice", df["Close"].iloc[-1])
        
        # حساب التغير السعري الفعلي الحالي للسهم في السوق
        price_change_ratio = (df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2]
        
        # 2. سحب آخر خبر حقيقي للشركة من الإنترنت تلقائياً
        news_list = stock.news
        if news_list and len(news_list) > 0:
            fetched_news = news_list[0].get('title', info_dict["backup_news"])
        else:
            fetched_news = info_dict["backup_news"]
            
        status = "متصل بالإنترنت بالكامل (أسعار وأخبار حية)"
        return float(live_price), fetched_news, float(price_change_ratio), status
        
    except Exception:
        status = "بيانات السوق الافتراضية المحفوظة (Offline)"
        np.random.seed(42)
        mock_change = np.random.choice([-0.012, 0.015, 0.008])
        return float(info_dict["backup_price"]), info_dict["backup_news"], mock_change, status


# ==========================================
# عرض النتائج عند الضغط على الزر
# ==========================================
if run_analysis:
    with st.spinner("الذك
