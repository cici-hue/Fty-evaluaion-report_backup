import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import base64

# ==================== 页面配置 & 现代感样式 ====================
st.set_page_config(
    page_title="工厂流程审核评分系统",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义现代感CSS
def add_custom_css():
    st.markdown("""
    <style>
    /* 整体样式优化 */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* 卡片样式 */
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    /* 按钮样式 */
    .stButton>button {
        border-radius: 8px;
        height: 40px;
        font-weight: 600;
        background-color: #4CAF50;
        color: white;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    /* 输入框样式 */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stDateInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        box-shadow: 2px 0 10px rgba(0,0,0,0.03);
    }
    /* 展开框样式 */
    [data-testid="stExpander"] {
        border-radius: 12px;
        background-color: white;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    /* 标题样式 */
    h1, h2, h3, h4 {
        color: #1e293b;
        font-weight: 600;
    }
    /* 橙色重点文字 */
    .orange-text {
        color: #f97316;
        font-weight: 500;
    }
    /* 菜单样式 */
    .stSidebar>div>div>div>button {
        font-weight: 600;
        color: #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# ==================== 数据初始化 ====================
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ==================== 完整8大项评分体系数据模型 ====================
class DataStore:
    def __init__(self):
        self.users = [{"id": 1, "username": "admin", "password": "admin123", "name": "管理员"}]
        self.factories = [
            {"id": 1, "name": "深圳XX服装厂"}, 
            {"id": 2, "name": "广州XX制衣厂"},
            {"id": 3, "name": "东莞XX服饰厂"},
            {"id": 4, "name": "佛山XX针织厂"}
        ]
        self.modules = self._init_modules()
        self.evaluations = self._load_evaluations()
        self.total_system_score = 177  # 总分177

    def _init_modules(self):
        """完整的8大项评估体系"""
        return {
            # 1. 纸样、样衣制作 (14分)
            "纸样、样衣制作": {
                "total_score": 14,
                "sub_modules": {
                    "纸样开发标准": {
                        "total_score": 6,
                        "items": [
                            {"id": "p1_1", "name": "使用CAD软件制作/修改纸样", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "p1_2", "name": "缝份清晰标记应合规", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "p1_3", "name": "布纹线，剪口标注合规并清晰", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "p1_4", "name": "放码标准（尺寸增量）遵守客户要求，并文档化", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "p1_5", "name": "技术包（Tech Pack）应明确标注尺寸表、工艺说明与特殊工艺说明", "score": 3, "is_key": True, "details": [], "comment": "清晰的技术包可确保生产符合客户要求，减少返工"},
                        ]
                    },
                    # Other modules are omitted for brevity...
                }
            },
            # More modules can be defined here...
        }

    def _load_evaluations(self):
        f = os.path.join(DATA_DIR, "evaluations.json")
        return json.load(open(f, 'r', encoding='utf-8')) if os.path.exists(f) else []

    def _save_evaluations(self):
        with open(os.path.join(DATA_DIR, "evaluations.json"), 'w', encoding='utf-8') as f:
            json.dump(self.evaluations, f, ensure_ascii=False, indent=2)

    def add_evaluation(self, ev):
        ev['id'] = len(self.evaluations) + 1
        ev['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.evaluations.append(ev)
        self._save_evaluations()
        return ev

# ==================== 页面路由 ====================
def main():
    # 登录页
    if 'user' not in st.session_state:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.title("🏭 工厂流程审核评分系统")
        st.markdown("### 系统登录", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            
            login_col1, login_col2 = st.columns(2)
            with login_col1:
                if st.button("登录", type="primary", use_container_width=True):
                    if next((u for u in db.users if u['username'] == username and u['password'] == password), None):
                        st.session_state['user'] = username
                        st.success("登录成功！正在跳转...")
                        st.rerun()
                    else:
                        st.error("用户名或密码错误")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # 主界面侧边栏
    st.sidebar.markdown("<h2 style='text-align: center;'>📊 审核系统</h2>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align: center; color: #64748b;'>当前用户：{st.session_state['user']}</p>", unsafe_allow_html=True)
    st.sidebar.divider()
    
    menu = st.sidebar.radio(
        "功能菜单", 
        ["开始评估", "历史记录", "对比分析"],
        index=0,
        format_func=lambda x: f"📝 {x}" if x == "开始评估" else f"📋 {x}" if x == "历史记录" else f"📈 {x}"
    )
    
    if menu == "开始评估":
        start_evaluation()
    elif menu == "历史记录":
        show_history()
    elif menu == "对比分析":
        show_comparison()

# ==================== 核心评估页面 ====================
def start_evaluation():
    st.markdown("<h2 style='margin-bottom: 20px;'>开始评估</h2>", unsafe_allow_html=True)
    
    # 评估基本信息
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("### 基本信息", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        factory_id = st.selectbox("工厂", [(f['id'], f['name']) for f in db.factories], format_func=lambda x: x[1])[0]
    with col2:
        eval_date = st.date_input("日期", date.today())
    with col3:
        evaluator = st.text_input("评估人员", value=st.session_state['user'], placeholder="请输入评估人员姓名")
    with col4:
        eval_type = st.selectbox("评估类型", ["常规审核", "整改复查"])

    st.markdown("</div>", unsafe_allow_html=True)

    # 其他逻辑代码...

if __name__ == "__main__":
    db = DataStore()
    main()
