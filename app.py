import numpy as np
import pandas as pd
import streamlit as st
import textblob
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from textblob import TextBlob

# ==========================================
# 1. إعدادات الصفحة والتصميم العام
# ==========================================
st.set_page_config(
    page_title="مستشار الإنماء الذكي (XAI)", layout="wide"
)

st.markdown(
    """
    <style>
    .main-title { text-align: center; color: #0056b3; font-family: 'Arial'; font-weight: bold; }
    .sub-title { text-align: center; color: #555555; margin-bottom: 30px; }
    .metric-box { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #0056b3; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 class='main-title'>منصة آفاق المستقبل | مستشار الاستثمار الذكي التفسيري (XAI)</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='sub-title'>دمج الذكاء الاصطناعي لمعالجة اللغات الطبيعية (NLP) مع التحليل الفني للأسهم السعودية</p>",
    unsafe_allow_html=True,
)

# دالة جلب البيانات خارج كتلة الأعمدة لتكون قابلة للاستدعاء ديناميكياً
@st.cache_data
def load_stock_data(ticker):
    data = yf.download(ticker, period="1mo", interval="1d")
    return data

# ==========================================
# 2. واجهة المستخدم واختيار الشركة
# ==========================================
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("مدخلات النظام اللحظية")

    # قائمة اختيار الشركة
    stock_selection = st.selectbox(
        "اختر الشركة للتحليل:", 
        ["مصرف الإنماء", "مصرف الراجحي", "أرامكو السعودية"]
    )

    # ربط الخيار بالرمز الصحيح
    ticker_mapping = {
        "مصرف الإنماء": "1150.SR",
        "مصرف الراجحي": "1120.SR",
        "أرامكو السعودية": "2222.SR"
    }
    ticker_symbol = ticker_mapping[stock_selection]

    # ==========================================
    # 3. جلب وتحديث السعر حياً بناءً على الرمز المختار
    # ==========================================
    try:
        stock_df = load_stock_data(ticker_symbol)
        latest_price = float(stock_df["Close"].iloc[-1])
        price_change = float(
            stock_df["Close"].iloc[-1] - stock_df["Close"].iloc[-2]
        )
    except Exception as e:
        latest_price = 24.50
        price_change = 0.00
        stock_df = pd.DataFrame(
            {"Close": [24.0, 24.2, 24.3, 24.50]},
            index=pd.date_range(end=pd.Timestamp.now(), periods=4),
        )

    # عرض سعر السهم المختار حالياً بعد التحديث
    st.metric(
        label=f"السعر الحالي لـ {stock_selection}",
        value=f"{latest_price:.2f} ر.س",
        delta=f"{price_change:+.2f} ر.س",
    )

    # إدخال الخبر المالي وتحليله
    st.write("---")
    st.write("تحليل نبرة آخر الأخبار المالية:")
    news_headline = st.text_area(
        "أدخل عنوان الخبر المالي المحرك للسوق باللغة الإنجليزية حالياً:",
        "The company announced excellent financial results with higher revenue growth than estimated this quarter.",
    )

    blob = TextBlob(news_headline)
    sentiment_score = blob.sentiment.polarity

    if sentiment_score > 0.1:
        sentiment_label = "إيجابي (Positive)"
        sentiment_color = "green"
    elif sentiment_score < -0.1:
        sentiment_label = "سلبي (Negative)"
        sentiment_color = "red"
    else:
        sentiment_label = "محايد (Neutral)"
        sentiment_color = "orange"

    st.markdown(
        f"نبرة الخبر المقدرة: <b style='color:{sentiment_color};'>{sentiment_label}</b>",
        unsafe_allow_html=True,
    )

with col2:
    st.subheader(f"حركة سهم {stock_selection} التاريخية (آخر شهر)")
    # الرسم البياني يتغير الآن تلقائياً مع السعر
    st.line_chart(stock_df["Close"])

# ==========================================
# 4. محرك الذكاء الاصطناعي التفسيري (XAI)
# ==========================================
st.write("---")
st.subheader("قرارات ومبررات الذكاء الاصطناعي التفسيري (XAI)")

news_weight = 0.60
price_weight = 0.40

technical_signal = 1 if price_change >= 0 else 0
sentiment_signal = 1 if sentiment_score >= 0 else 0

final_score = (sentiment_signal * news_weight) + (technical_signal * price_weight)

if final_score >= 0.6:
    decision = "توصية: شراء / احتفاظ (Buy / Hold)"
    decision_color = "#28a745"
elif final_score <= 0.4:
    decision = "توصية: حذر / بيع (Sell / Caution)"
    decision_color = "#dc3545"
else:
    decision = "توصية: مراقبة السوق (Monitor / Neutral)"
    decision_color = "#ffc107"

st.markdown(
    f"<div style='background-color:{decision_color}; padding:15px; border-radius:8px; color:white; font-size:20px; font-weight:bold; text-align:center;'>{decision}</div>",
    unsafe_allow_html=True,
)

st.write("")
with st.container():
    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
    st.write("لماذا اتخذ الذكاء الاصطناعي هذا القرار؟ (شفافية التفسير XAI):")
    st.write(
        f"- عامل نبرة الأخبار ({news_weight*100}%): يعتمد النظام حالياً على معالجة النص المدخل دلالياً وحصل الخبر على تقييم نبرة بمعدل ({sentiment_score:.2f})."
    )
    st.write(
        f"- عامل زخم السعر الفني ({price_weight*100}%): تم رصد آخر تحرك سعري في تداول بمعدل تغير قدره ({price_change:+.2f} ر.س)."
    )
    st.write(
        "بناءً على هذه الأوزان المشتركة، تم فك غموض 'الصندوق الأسود' ليوضح للمستثمر الفرد المبتدئ سبب التوصية دون توجيه أعمى."
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 5. ذيل الصفحة (إخلاء المسؤولية القانونية)
# ==========================================
st.write("")
st.markdown(
    "<hr><p style='text-align: center; font-size: 11px; color: gray;'>تنبيه قانوني: هذا التطبيق هو نموذج أولي (Prototype) لأغراض مسابقة هاكاثون أمد التعليمية، ولا يمثل نصيحة مالية حقيقية ومباشرة لشراء أو بيع الأوراق المالية.</p>",
    unsafe_allow_html=True,
)
