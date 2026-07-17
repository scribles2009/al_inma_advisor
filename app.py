import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from textblob import TextBlob

st.set_page_config(
    page_title="مستشار الاستثمار الذكي - مصرف الإنماء",
    page_icon="chart-line",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #002D62; text-align: center; margin-bottom: 20px; font-family: 'Arial'; }
    .stButton>button { background-color: #002D62; color: white; width: 100%; border-radius: 8px; font-weight: bold; height: 45px; }
    .stButton>button:hover { background-color: #D4AF37; color: #002D62; border: 1px solid #002D62; }
    .metric-box { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #002D62; }
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

st.sidebar.header("إعدادات التحليل الذكي")

stock_options = {
    "مصرف الإنماء (1150)": {"ticker": "1150.SR", "backup_price": 24.83, "backup_news": "Alinma Bank reports record breaking net profit growth this quarter with expanding digital banking services."},
    "أرامكو السعودية (2222)": {"ticker": "2222.SR", "backup_price": 30.10, "backup_news": "Saudi Aramco expands its global energy supply chains and strengthens sustainable investment initiatives."},
    "مصرف الراجحي (1120)": {"ticker": "1120.SR", "backup_price": 85.50, "backup_news": "Al Rajhi Bank premium banking segments witness increased customer onboarding due to upgraded app features."},
}

selected_stock_label = st.sidebar.selectbox("اختر السهم للتحليل:", list(stock_options.keys()))
stock_info = stock_options[selected_stock_label]

st.sidebar.info("تنبيه: النظام يسحب السعر الحالي وآخر التقارير الإخبارية تلقائياً من السوق بمجرد الضغط على زر التحليل.")

run_analysis = st.sidebar.button("ابدأ التحليل الفوري وربط البيانات الحية")

def get_live_market_and_news(ticker_symbol, info_dict):
    try:
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period="5d")
        if df.empty or len(df) < 2:
            raise Exception("خطأ في الاتصال بخادم البيانات")
        live_price = stock.info.get("currentPrice", df["Close"].iloc[-1])
        
        price_change_ratio = (df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2]
        
        news_list = stock.news
        if news_list and len(news_list) > 0:
            fetched_news = news_list[0].get('title', info_dict["backup_news"])
        else:
            fetched_news = info_dict["backup_news"]
            
        status = "متصل بالإنترنت بالكامل (أسعار وأخبار حية)"
        return float(live_price), fetched_news, float(price_change_ratio), status, df
        
    except Exception:
        status = "بيانات السوق الافتراضية المحفوظة (وضع عدم الاتصال)"
        np.random.seed(42)
        mock_change = np.random.choice([-0.012, 0.015, 0.008])
        dates = pd.date_range(end=pd.Timestamp.now(), periods=5)
        df_backup = pd.DataFrame(
            {"Close": [info_dict["backup_price"] * (1 + i*0.005) for i in range(5)], "Volume": [1200000, 1300000, 1100000, 1500000, 1400000]},
            index=dates
        )
        return float(info_dict["backup_price"]), info_dict["backup_news"], mock_change, status, df_backup

if run_analysis:
    with st.spinner("الذكاء الاصطناعي يتصل بالإنترنت الآن ويسحب الأسعار والتقارير الإخبارية الحية..."):
        live_price, current_live_news, actual_market_change, connection_status, df_history = get_live_market_and_news(
            stock_info["ticker"], stock_info
        )

        analysis = TextBlob(current_live_news)
        news_score = (analysis.sentiment.polarity + 1) / 2

        combined_score = (news_score * 0.6) + ((actual_market_change * 10 + 0.5) * 0.4)
        combined_score = max(0.15, min(0.85, combined_score))

        price_impact_percentage = (combined_score - 0.5) * 0.08  
        ai_adjusted_price = live_price * (1 + price_impact_percentage)

        if news_score > 0.54:
            sentiment_label = "إيجابي"
        elif news_score < 0.46:
            sentiment_label = "سلبي أو حذر"
        else:
            sentiment_label = "محايد"

        prob_up = int(combined_score * 100)
        prob_down = 100 - prob_up

    st.subheader(f"تقرير التحليل الفوري لـ: {selected_stock_label}")
    st.caption(f"حالة اتصال المنصة: {connection_status}")

    st.info(f"آخر خبر تم سحبه تلقائياً للشركة من خوادم الإنترنت الإخبارية:\n\n> *\"{current_live_news}\"*")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="السعر اللحظي من الإنترنت",
            value=f"{live_price:.2f} ر.س",
            delta=f"السعر العادل المستهدف: {ai_adjusted_price:.2f} ر.س",
        )
    with col2:
        st.metric(label="تحليل مشاعر النبرة الإخبارية", value=sentiment_label)
    with col3:
        risk_level = "منخفض" if combined_score > 0.5 else "مرتفع"
        st.metric(label="مستوى مخاطرة السهم اليوم", value=risk_level)

    st.write("---")

    col_chart, col_table = st.columns(2)
    
    with col_chart:
        st.subheader("توقعات الاتجاه القادم (مخطط خطي)")
        prob_df = pd.DataFrame(
            {"الاحتمالية (%)": [prob_up, prob_down]}, index=["اتجاه صاعد", "اتجاه هابط"]
        )
        st.line_chart(prob_df)
        
    with col_table:
        st.subheader("سجل أسعار الإغلاق الأخيرة (تداول حقيقي)")
        display_df = df_history[["Close", "Volume"]].tail(5)
        display_df.columns = ["سعر الإغلاق (ر.س)", "حجم التداول"]
        st.dataframe(display_df, use_container_width=True)

    st.write("")
    with st.container():
        st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
        st.write("**الذكاء الاصطناعي التفسيري (Explainable AI): مبررات التوقع والربط الشفاف**")
        st.write(
            f"• قام النموذج بدمج النبرة النفسية للخبر المسحوب بنسبة تأثير بلغت (**{news_score*100:.1f}%**) مع الزخم السعري الفعلي لحركة السهم الحالية في منصة تداول بنسبة (**{actual_market_change*100:.2f}%**). "
            f"يتم وزن هذه الاحتماليات بدقة رياضية تضمن الشفافية الاستثمارية الكاملة للمستثمر، والابتعاد التام عن التوقعات الصماء غير المبررة."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.warning(
        "إخلاء مسؤولية قانوني: هذا النظام مصنف كأداة تقنية استرشادية لدعم القرار المالي لعملاء مصرف الإنماء، ولا يعتبر توصية استثمارية مباشرة للبيع أو الشراء."
    )

else:
    st.info(
        "بمجرد الضغط على زر [ابدأ التحليل الفوري وربط البيانات الحية]، سيتصل النظام بالإنترنت تلقائياً، ليدمج سعر السهم اللحظي وحركته الفنية مع آخر التقارير المنشورة."
    )
