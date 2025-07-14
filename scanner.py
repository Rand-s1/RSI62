import requests
import ta
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import time
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 设置页面配置
st.set_page_config(
    page_title="RSI6 扫描器",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# iOS风格CSS样式 - 修复版本
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
    
    /* 全局样式 */
    * {
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* 检测深色模式 */
    :root {
        --bg-primary: #f5f7fa;
        --bg-secondary: #ffffff;
        --text-primary: #1d1d1f;
        --text-secondary: #86868b;
        --card-bg: rgba(255, 255, 255, 0.85);
        --card-border: rgba(255, 255, 255, 0.2);
        --shadow: rgba(0, 0, 0, 0.08);
        --blue: #007AFF;
        --green: #34C759;
        --red: #FF3B30;
        --orange: #FF9500;
    }
    
    /* 深色模式变量 */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #1c1c1e;
            --bg-secondary: #2c2c2e;
            --text-primary: #ffffff;
            --text-secondary: #8e8e93;
            --card-bg: rgba(44, 44, 46, 0.85);
            --card-border: rgba(84, 84, 88, 0.3);
            --shadow: rgba(0, 0, 0, 0.3);
            --blue: #0A84FF;
            --green: #30D158;
            --red: #FF453A;
            --orange: #FF9F0A;
        }
    }
    
    /* 强制深色模式支持 */
    [data-theme="dark"] {
        --bg-primary: #1c1c1e;
        --bg-secondary: #2c2c2e;
        --text-primary: #ffffff;
        --text-secondary: #8e8e93;
        --card-bg: rgba(44, 44, 46, 0.85);
        --card-border: rgba(84, 84, 88, 0.3);
        --shadow: rgba(0, 0, 0, 0.3);
        --blue: #0A84FF;
        --green: #30D158;
        --red: #FF453A;
        --orange: #FF9F0A;
    }
    
    /* 主容器 */
    .main {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        padding: 1rem;
        min-height: 100vh;
        color: var(--text-primary);
    }
    
    /* 平滑滚动 */
    html {
        scroll-behavior: smooth;
    }
    
    .main .block-container {
        max-width: 100%;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Streamlit 容器背景 */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    }
    
    /* iOS风格标题 */
    .ios-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary) !important;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .ios-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        color: var(--text-secondary) !important;
        text-align: center;
        margin-bottom: 0;
    }
    
    /* iOS风格卡片 */
    .ios-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--card-border);
        box-shadow: 0 8px 32px var(--shadow);
        color: var(--text-primary);
    }
    
    /* 卡片内的标题和文本 */
    .ios-card h3, .ios-card h4 {
        color: var(--text-primary) !important;
        font-weight: 600;
    }
    
    .ios-card p, .ios-card li {
        color: var(--text-primary) !important;
        line-height: 1.6;
    }
    
    .ios-card strong {
        color: var(--text-primary) !important;
    }
    
    /* iOS风格按钮 */
    .stButton > button {
        background: linear-gradient(135deg, var(--blue) 0%, #0051D5 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
        letter-spacing: 0.3px;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
        background: linear-gradient(135deg, #0056D6 0%, #003DB3 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* iOS风格指标卡片 */
    .ios-metric {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid var(--card-border);
        box-shadow: 0 4px 16px var(--shadow);
        transition: transform 0.2s ease;
        color: var(--text-primary);
    }
    
    .ios-metric:hover {
        transform: translateY(-2px);
    }
    
    .ios-metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin-bottom: 0.25rem;
    }
    
    .ios-metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background: var(--card-bg) !important;
        backdrop-filter: blur(20px);
        border-radius: 0 16px 16px 0;
        color: var(--text-primary);
    }
    
    .sidebar .sidebar-content .block-container {
        padding-top: 2rem;
    }
    
    /* 侧边栏标签和文本 */
    .sidebar label {
        color: var(--text-primary) !important;
    }
    
    .sidebar .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    /* 数据表格iOS风格 */
    .dataframe {
        background: var(--card-bg) !important;
        backdrop-filter: blur(20px);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--card-border);
        box-shadow: 0 4px 16px var(--shadow);
    }
    
    /* 表格内容颜色 */
    .dataframe table {
        color: var(--text-primary) !important;
    }
    
    .dataframe th {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    .dataframe td {
        color: var(--text-primary) !important;
    }
    
    /* 输入框样式 */
    .stNumberInput > div > div > input {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 8px;
        padding: 0.5rem;
        transition: all 0.2s ease;
        color: var(--text-primary) !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
    }
    
    .stSelectbox > div > div > select {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 8px;
        padding: 0.5rem;
        transition: all 0.2s ease;
        color: var(--text-primary) !important;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
    }
    
    /* 标签颜色 */
    .stNumberInput label, .stSelectbox label {
        color: var(--text-primary) !important;
    }
    
    /* 进度条样式 - 修复重复显示 */
    .stProgress {
        margin: 1rem 0;
    }
    
    .stProgress > div {
        background-color: rgba(0, 0, 0, 0.1);
        border-radius: 6px;
        height: 6px;
        overflow: hidden;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--blue), #0051D5);
        border-radius: 6px;
        height: 100%;
        transition: width 0.3s ease;
    }
    
    /* 警告和信息框 */
    .stAlert {
        border-radius: 12px;
        backdrop-filter: blur(20px);
        border: 1px solid var(--card-border);
        color: var(--text-primary) !important;
        margin: 1rem 0;
    }
    
    /* 成功消息 */
    .stSuccess {
        background: rgba(52, 199, 89, 0.1) !important;
        border: 1px solid var(--green) !important;
        color: var(--green) !important;
    }
    
    /* 信息消息 */
    .stInfo {
        background: rgba(0, 122, 255, 0.1) !important;
        border: 1px solid var(--blue) !important;
        color: var(--blue) !important;
    }
    
    /* 警告消息 */
    .stWarning {
        background: rgba(255, 149, 0, 0.1) !important;
        border: 1px solid var(--orange) !important;
        color: var(--orange) !important;
    }
    
    /* 错误消息 */
    .stError {
        background: rgba(255, 59, 48, 0.1) !important;
        border: 1px solid var(--red) !important;
        color: var(--red) !important;
    }
    
    /* 下载按钮样式 */
    .stDownloadButton > button {
        background: var(--green) !important;
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        background: #30D158 !important;
        transform: translateY(-1px);
    }
    
    /* Checkbox 样式 */
    .stCheckbox > label {
        color: var(--text-primary) !important;
        font-weight: 500;
    }
    
    /* Expander 样式 */
    .streamlit-expanderHeader {
        background: var(--card-bg) !important;
        border-radius: 8px;
        border: 1px solid var(--card-border) !important;
        color: var(--text-primary) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        color: var(--text-primary) !important;
    }
    
    /* Spinner 样式 */
    .stSpinner {
        color: var(--blue) !important;
    }
    
    /* 文本颜色强制设置 */
    .stMarkdown, .stText {
        color: var(--text-primary) !important;
    }
    
    /* 强制设置所有文本元素 */
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: var(--text-primary) !important;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .ios-title {
            font-size: 2rem;
        }
        .ios-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .ios-metric {
            padding: 0.75rem;
        }
        .ios-metric-value {
            font-size: 1.5rem;
        }
    }
</style>

<script>
// 检测系统主题并应用
function detectTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
    }
}

// 监听主题变化
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addListener(detectTheme);
}

// 初始化主题
detectTheme();
</script>
""", unsafe_allow_html=True)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置常量
class Config:
    ENDPOINTS = ["https://api.bitget.com"]
    PRODUCT_TYPE = "usdt-futures"
    LIMIT = 100
    RSI_PERIOD = 6
    SLEEP_BETWEEN_REQUESTS = 0.5
    MAX_WORKERS = 10
    MIN_CANDLES_RELIABLE = 20
    
    # UI配置
    TIMEFRAMES = {
        "1小时": "1H",
        "4小时": "4H", 
        "1天": "1D"
    }
    
    # RSI区间配置
    RSI_RANGES = {
        "超卖区域": (0, 30),
        "中性区域": (30, 70),
        "超买区域": (70, 100)
    }

def create_header():
    """创建iOS风格页面头部"""
    st.markdown("""
    <div class="ios-card">
        <h1 class="ios-title">📱 RSI6 扫描器</h1>
        <p class="ios-subtitle">专业的加密货币技术分析工具</p>
    </div>
    """, unsafe_allow_html=True)

def create_sidebar():
    """创建iOS风格侧边栏"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0 2rem 0;">
            <h3 style="font-weight: 600; margin: 0;">⚙️ 扫描设置</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 时间框架选择
        timeframe_display = st.selectbox(
            "📊 时间框架",
            options=list(Config.TIMEFRAMES.keys()),
            index=1,  # 默认4小时
            help="选择K线时间周期"
        )
        timeframe = Config.TIMEFRAMES[timeframe_display]
        
        st.markdown("""
        <div style="padding: 1rem 0;">
            <h4 style="font-weight: 600; margin-bottom: 1rem;">🎯 RSI阈值设置</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # RSI阈值设置
        col1, col2 = st.columns(2)
        with col1:
            rsi_low = st.number_input(
                "超卖线", 
                min_value=0.0, 
                max_value=50.0, 
                value=10.0, 
                step=1.0,
                help="RSI低于此值显示超卖信号"
            )
        with col2:
            rsi_high = st.number_input(
                "超买线", 
                min_value=50.0, 
                max_value=100.0, 
                value=90.0, 
                step=1.0,
                help="RSI高于此值显示超买信号"
            )
        
        # 高级设置
        with st.expander("🔧 高级设置"):
            show_charts = st.checkbox("显示图表分析", value=True)
            min_volume = st.number_input("最小成交量过滤", value=0.0, help="过滤低成交量币种")
            
        return timeframe, rsi_low, rsi_high, show_charts, min_volume

def create_ios_statistics_cards(results: List[dict], total_symbols: int):
    """创建iOS风格统计卡片"""
    oversold = len([r for r in results if r["rsi6"] < 30])
    overbought = len([r for r in results if r["rsi6"] > 70])
    gainers = len([r for r in results if r["change (%)"] > 0])
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics_data = [
        (col1, "📊", total_symbols, "总扫描数"),
        (col2, "🔥", overbought, "超买信号"),
        (col3, "💎", oversold, "超卖信号"),
        (col4, "📈", gainers, "上涨币种")
    ]
    
    for col, icon, value, label in metrics_data:
        with col:
            st.markdown(f"""
            <div class="ios-metric">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <div class="ios-metric-value">{value}</div>
                <div class="ios-metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def create_ios_section_header(title: str, subtitle: str = ""):
    """创建iOS风格章节标题"""
    st.markdown(f"""
    <div class="ios-card">
        <h2 style="font-weight: 600; margin-bottom: 0.5rem;">{title}</h2>
        {f'<p style="margin: 0; font-size: 0.95rem; opacity: 0.8;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def create_guide_section():
    """创建使用指南 - 修复HTML显示问题"""
    st.markdown("### 🎯 使用指南")
    
    st.markdown("**RSI6扫描器**是一个专业的技术分析工具，帮助您快速找到具有极端RSI值的交易机会。")
    
    st.markdown("#### 📊 功能特点")
    st.markdown("""
    - 🔄 **实时扫描**: 并行处理所有USDT永续合约
    - 📈 **多时间框架**: 支持1H、4H、1D级别分析  
    - 🎨 **可视化分析**: 直观的图表和统计信息
    - 📁 **数据导出**: 支持CSV格式下载
    """)
    
    st.markdown("#### 🎯 交易信号")
    st.markdown("""
    - 🟢 **超卖信号** (RSI < 30): 可能的买入机会
    - 🔴 **超买信号** (RSI > 70): 可能的卖出机会
    - ⚠️ **数据提醒**: 自动标注K线数据不足的币种
    """)
    
    st.markdown("#### 🚀 开始使用")
    st.markdown("""
    1. 在左侧设置您的扫描参数
    2. 点击"开始扫描"按钮
    3. 等待扫描完成并查看结果
    4. 可选择下载数据进行进一步分析
    """)

# ... 保持其他函数不变 ...

def ping_endpoint(endpoint: str) -> bool:
    """测试端点是否可用"""
    url = f"{endpoint}/api/v2/mix/market/candles"
    params = {
        "symbol": "BTCUSDT",
        "granularity": "4H",
        "limit": 1,
        "productType": Config.PRODUCT_TYPE,
    }
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.status_code == 200 and r.json().get("code") == "00000"
    except:
        return False

def get_working_endpoint() -> str:
    """获取可用端点"""
    for ep in Config.ENDPOINTS:
        for _ in range(3):
            if ping_endpoint(ep):
                return ep
            time.sleep(1)
    raise RuntimeError("无可用端点，请检查网络连接")

def get_usdt_symbols(base: str) -> List[str]:
    """获取USDT永续合约交易对"""
    url = f"{base}/api/v2/mix/market/contracts"
    params = {"productType": Config.PRODUCT_TYPE}
    
    try:
        r = requests.get(url, params=params, timeout=5)
        j = r.json()
        if j.get("code") != "00000":
            raise RuntimeError(f"获取交易对失败: {j}")
        symbols = [c["symbol"] for c in j["data"]]
        logger.info(f"找到 {len(symbols)} 个USDT永续合约")
        return symbols
    except Exception as e:
        logger.error(f"获取交易对错误: {e}")
        raise

def fetch_candles(base: str, symbol: str, granularity: str) -> pd.DataFrame:
    """获取K线数据"""
    url = f"{base}/api/v2/mix/market/candles"
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "limit": Config.LIMIT,
        "productType": Config.PRODUCT_TYPE,
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        j = r.json()
        if j.get("code") != "00000":
            return pd.DataFrame()
            
        cols = ["ts", "open", "high", "low", "close", "volume_base", "volume_quote"]
        df = pd.DataFrame(j["data"], columns=cols)
        df[["open", "high", "low", "close", "volume_base", "volume_quote"]] = df[
            ["open", "high", "low", "close", "volume_base", "volume_quote"]
        ].astype(float)
        df["ts"] = pd.to_datetime(df["ts"].astype("int64"), unit="ms")
        return df.sort_values("ts").reset_index(drop=True)
    except Exception as e:
        logger.error(f"{symbol} K线获取失败: {e}")
        return pd.DataFrame()

def fetch_all_tickers(base: str) -> Dict[str, dict]:
    """批量获取ticker数据"""
    url = f"{base}/api/v2/mix/market/tickers"
    params = {"productType": Config.PRODUCT_TYPE}
    
    try:
        r = requests.get(url, params=params, timeout=5)
        j = r.json()
        
        logger.info(f"Ticker API响应: code={j.get('code')}, msg={j.get('msg')}")
        
        if j.get("code") != "00000":
            logger.error(f"API返回错误: {j}")
            return {}
            
        if not isinstance(j.get("data"), list):
            logger.error(f"API数据格式错误: {type(j.get('data'))}")
            return {}
        
        tickers = {}
        for item in j["data"]:
            try:
                if len(tickers) == 0:
                    logger.info(f"Ticker数据结构示例: {list(item.keys())}")
                
                symbol = item.get("symbol", "")
                if not symbol:
                    continue
                
                change24h = 0.0
                if "change24h" in item:
                    change24h = float(item["change24h"]) * 100
                elif "chgUtc" in item:
                    change24h = float(item["chgUtc"]) * 100
                elif "changeUtc24h" in item:
                    change24h = float(item["changeUtc24h"]) * 100
                
                volume = 0.0
                if "baseVolume" in item:
                    volume = float(item["baseVolume"])
                elif "baseVol" in item:
                    volume = float(item["baseVol"])
                elif "vol24h" in item:
                    volume = float(item["vol24h"])
                
                price = 0.0
                if "close" in item:
                    price = float(item["close"])
                elif "last" in item:
                    price = float(item["last"])
                elif "lastPr" in item:
                    price = float(item["lastPr"])
                
                tickers[symbol] = {
                    "change24h": change24h,
                    "volume": volume,
                    "price": price
                }
                
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"处理ticker数据失败 {item.get('symbol', 'unknown')}: {e}")
                continue
        
        logger.info(f"成功获取 {len(tickers)} 个ticker数据")
        return tickers
        
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求失败: {e}")
        return {}
    except Exception as e:
        logger.error(f"获取ticker数据失败: {e}")
        return {}

def calculate_rsi_and_metrics(df: pd.DataFrame) -> Tuple[Optional[float], int, dict]:
    """计算RSI和其他技术指标"""
    try:
        close_series = pd.Series(df["close"].astype(float)).reset_index(drop=True)
        candle_count = len(close_series)
        
        if candle_count < Config.RSI_PERIOD + 1:
            return None, candle_count, {}
            
        rsi_series = ta.momentum.RSIIndicator(close=close_series, window=Config.RSI_PERIOD).rsi()
        rsi = rsi_series.iloc[-1]
        
        metrics = {
            "sma_20": ta.trend.sma_indicator(close_series, window=20).iloc[-1] if candle_count >= 20 else None,
            "volatility": close_series.pct_change().std() * 100,
            "price_change": ((close_series.iloc[-1] - close_series.iloc[-2]) / close_series.iloc[-2]) * 100 if candle_count >= 2 else 0
        }
        
        return rsi, candle_count, metrics
        
    except Exception as e:
        logger.error(f"指标计算错误: {e}")
        return None, 0, {}

def fetch_candles_wrapper(args) -> tuple:
    """并行获取K线数据的包装函数"""
    base, symbol, granularity = args
    df = fetch_candles(base, symbol, granularity)
    if not df.empty:
        df["symbol"] = symbol
    return symbol, df

def create_rsi_distribution_chart(results: List[dict]):
    """创建RSI分布图表 - 深色模式适配"""
    if not results:
        return None
        
    df = pd.DataFrame(results)
    
    fig = px.histogram(
        df, 
        x="rsi6", 
        nbins=20,
        title="RSI6 分布图",
        labels={"rsi6": "RSI6 值", "count": "币种数量"},
        color_discrete_sequence=["#007AFF"]
    )
    
    fig.add_vline(x=30, line_dash="dash", line_color="#34C759", annotation_text="超卖线 (30)")
    fig.add_vline(x=70, line_dash="dash", line_color="#FF3B30", annotation_text="超买线 (70)")
    
    fig.update_layout(
        template="plotly_dark",
        height=400,
        showlegend=False,
        font=dict(family="SF Pro Display, -apple-system, BlinkMacSystemFont", color="#ffffff"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_color="#ffffff"
    )
    
    return fig

def create_scatter_plot(results: List[dict]):
    """创建RSI vs 涨跌幅散点图 - 深色模式适配"""
    if not results:
        return None
        
    df = pd.DataFrame(results)
    
    def get_color(rsi):
        if rsi < 30:
            return "超卖"
        elif rsi > 70:
            return "超买" 
        else:
            return "中性"
    
    df["rsi_zone"] = df["rsi6"].apply(get_color)
    
    fig = px.scatter(
        df,
        x="rsi6",
        y="change (%)",
        color="rsi_zone",
        title="RSI6 vs 24小时涨跌幅",
        labels={"rsi6": "RSI6 值", "change (%)": "24h涨跌幅 (%)"},
        hover_data=["symbol"],
        color_discrete_map={
            "超卖": "#34C759",
            "超买": "#FF3B30", 
            "中性": "#8E8E93"
        }
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="#8E8E93", annotation_text="涨跌分界线")
    fig.add_vline(x=30, line_dash="dash", line_color="#34C759")
    fig.add_vline(x=70, line_dash="dash", line_color="#FF3B30")
    
    fig.update_layout(
        template="plotly_dark",
        height=400,
        font=dict(family="SF Pro Display, -apple-system, BlinkMacSystemFont", color="#ffffff"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_color="#ffffff"
    )
    
    return fig

def format_dataframe(df: pd.DataFrame, is_gainer: bool = True) -> pd.DataFrame:
    """格式化数据框显示"""
    if df.empty:
        return df
        
    def add_trend_icon(row):
        change = row["change (%)"]
        rsi = row["rsi6"]
        
        if change > 5:
            trend = "🚀"
        elif change > 0:
            trend = "📈"
        elif change > -5:
            trend = "📉"
        else:
            trend = "💥"
            
        return f"{trend} {row['symbol']}"
    
    df_formatted = df.copy()
    df_formatted["交易对"] = df.apply(add_trend_icon, axis=1)
    df_formatted["24h涨跌"] = df_formatted["change (%)"].apply(lambda x: f"{x:+.2f}%")
    df_formatted["RSI6"] = df_formatted["rsi6"].apply(lambda x: f"{x:.1f}")
    df_formatted["K线数"] = df_formatted["k_lines"]
    df_formatted["备注"] = df_formatted["note"]
    
    return df_formatted[["交易对", "24h涨跌", "RSI6", "K线数", "备注"]]

def scan_symbols(base: str, symbols: List[str], granularity: str, rsi_low: float, rsi_high: float, min_volume: float = 0) -> Tuple[List[dict], dict]:
    """扫描交易对 - 修复进度条重复问题"""
    start_time = time.time()
    results = []
    
    with st.spinner("📊 正在获取市场数据..."):
        tickers = fetch_all_tickers(base)
        if not tickers:
            st.warning("⚠️ 无法获取完整的市场数据，将使用默认值")
            tickers = {}
    
    # 使用单一的进度条容器
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    candle_data = {}
    total_symbols = len(symbols)
    processed = 0
    
    with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
        futures = [executor.submit(fetch_candles_wrapper, (base, symbol, granularity)) for symbol in symbols]
        
        for future in as_completed(futures):
            symbol, df = future.result()
            processed += 1
            
            if not df.empty:
                candle_data[symbol] = df
                
            # 更新进度 - 使用单一容器
            progress = processed / total_symbols
            progress_placeholder.progress(progress, text=f"🔄 获取K线数据: {processed}/{total_symbols}")
            status_placeholder.info(f"⏱️ 正在处理: {symbol}")
    
    # 清除进度显示
    progress_placeholder.empty()
    status_placeholder.empty()
    
    with st.spinner("🧮 正在计算技术指标..."):
        insufficient_data = []
        
        for symbol in symbols:
            try:
                if symbol not in candle_data:
                    continue
                    
                df = candle_data[symbol]
                rsi, candle_count, metrics = calculate_rsi_and_metrics(df)
                
                if rsi is None:
                    insufficient_data.append(symbol)
                    continue
                
                ticker_data = tickers.get(symbol, {
                    "change24h": 0, 
                    "volume": 0, 
                    "price": 0
                })
                
                if ticker_data["volume"] < min_volume:
                    continue
                
                if rsi < rsi_low or rsi > rsi_high:
                    note = ""
                    if candle_count < Config.MIN_CANDLES_RELIABLE:
                        note = f"数据较少({candle_count}根)"
                    
                    results.append({
                        "symbol": symbol,
                        "change (%)": round(ticker_data["change24h"], 2),
                        "rsi6": round(rsi, 2),
                        "k_lines": candle_count,
                        "note": note,
                        "volume": ticker_data["volume"],
                        "price": ticker_data["price"],
                        "volatility": metrics.get("volatility", 0)
                    })
                    
            except Exception as e:
                logger.warning(f"{symbol} 处理失败: {e}")
                continue
    
    scan_stats = {
        "scan_time": time.time() - start_time,
        "total_symbols": total_symbols,
        "processed_symbols": len(candle_data),
        "insufficient_data": len(insufficient_data),
        "results_count": len(results)
    }
    
    return results, scan_stats

def main():
    create_header()
    
    timeframe, rsi_low, rsi_high, show_charts, min_volume = create_sidebar()
    
    col1, col2 = st.columns([4, 1])
    
    with col2:
        st.markdown("""
        <div class="ios-card">
            <h4 style="font-weight: 600; margin-bottom: 1rem;">🚀 开始扫描</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("开始扫描", key="scan_button"):
            scan_pressed = True
        else:
            scan_pressed = False
            
        st.markdown(f"""
        <div class="ios-card">
            <h4 style="font-weight: 600; margin-bottom: 1rem;">📋 当前设置</h4>
            <div style="line-height: 1.6; opacity: 0.8;">
                <p style="margin-bottom: 0.5rem;"><strong>时间框架:</strong> {timeframe}</p>
                <p style="margin-bottom: 0.5rem;"><strong>超卖线:</strong> {rsi_low}</p>
                <p style="margin-bottom: 0.5rem;"><strong>超买线:</strong> {rsi_high}</p>
                {f'<p style="margin-bottom: 0.5rem;"><strong>最小成交量:</strong> {min_volume:,.0f}</p>' if min_volume > 0 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col1:
        if not scan_pressed:
            # 使用修复后的指南函数
            with st.container():
                st.markdown("""
                <div class="ios-card">
                """, unsafe_allow_html=True)
                
                create_guide_section()
                
                st.markdown("""
                </div>
                """, unsafe_allow_html=True)
            return
    
    if scan_pressed:
        try:
            with st.spinner("🔗 连接到Bitget API..."):
                base = get_working_endpoint()
                st.success("✅ API连接成功")
            
            with st.spinner("📋 获取交易对列表..."):
                symbols = get_usdt_symbols(base)
                st.success(f"✅ 找到 {len(symbols)} 个USDT永续合约")
            
            results, scan_stats = scan_symbols(base, symbols, timeframe, rsi_low, rsi_high, min_volume)
            
            st.success(f"✅ 扫描完成! 耗时 {scan_stats['scan_time']:.1f} 秒")
            
            if scan_stats['insufficient_data'] > 0:
                st.info(f"ℹ️ 有 {scan_stats['insufficient_data']} 个币种数据不足，已跳过")
            
            gainers = sorted([r for r in results if r["change (%)"] > 0], key=lambda x: x["rsi6"], reverse=True)
            losers = sorted([r for r in results if r["change (%)"] <= 0], key=lambda x: x["rsi6"])
            
            create_ios_statistics_cards(results, scan_stats['total_symbols'])
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            create_ios_section_header("🔥 超买区域", f"RSI6 {timeframe} > {rsi_high}")
            if gainers:
                gainers_df = pd.DataFrame(gainers)
                formatted_gainers = format_dataframe(gainers_df, True)
                st.dataframe(formatted_gainers, use_container_width=True, hide_index=True)
                
                csv_data = gainers_df.to_csv(index=False)
                st.download_button(
                    label="📥 下载超买数据 CSV",
                    data=csv_data,
                    file_name=f"overbought_rsi6_{timeframe}_{current_time.replace(' ', '_').replace(':', '-')}.csv",
                    mime="text/csv",
                    key="download_gainers"
                )
            else:
                st.info("🤔 当前没有符合条件的超买信号")
            
            create_ios_section_header("💎 超卖区域", f"RSI6 {timeframe} < {rsi_low}")
            if losers:
                losers_df = pd.DataFrame(losers)
                formatted_losers = format_dataframe(losers_df, False)
                st.dataframe(formatted_losers, use_container_width=True, hide_index=True)
                
                csv_data = losers_df.to_csv(index=False)
                st.download_button(
                    label="📥 下载超卖数据 CSV", 
                    data=csv_data,
                    file_name=f"oversold_rsi6_{timeframe}_{current_time.replace(' ', '_').replace(':', '-')}.csv",
                    mime="text/csv",
                    key="download_losers"
                )
            else:
                st.info("🤔 当前没有符合条件的超卖信号")
            
            if show_charts and results:
                create_ios_section_header("📊 数据分析", "可视化图表分析")
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    rsi_chart = create_rsi_distribution_chart(results)
                    if rsi_chart:
                        st.plotly_chart(rsi_chart, use_container_width=True)
                
                with chart_col2:
                    scatter_chart = create_scatter_plot(results)
                    if scatter_chart:
                        st.plotly_chart(scatter_chart, use_container_width=True)
                
            with st.expander("ℹ️ 扫描详情"):
                st.markdown(f"""
                **扫描时间**: {current_time}  
                **处理时间**: {scan_stats['scan_time']:.2f} 秒  
                **总交易对数**: {scan_stats['total_symbols']}  
                **成功处理**: {scan_stats['processed_symbols']}  
                **符合条件**: {scan_stats['results_count']}  
                **数据不足**: {scan_stats['insufficient_data']}
                """)
                
        except Exception as e:
            st.error(f"❌ 扫描过程中发生错误: {str(e)}")
            logger.error(f"扫描错误: {e}")

    st.markdown("""
    <div class="ios-card" style="text-align: center; margin-top: 2rem;">
        <p style="margin: 0; font-size: 0.9rem; opacity: 0.8;">📱 RSI6 扫描器 - iOS风格版本</p>
        <p style="margin: 0.25rem 0 0 0; font-size: 0.8rem; opacity: 0.6;">专业的加密货币技术分析工具</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
