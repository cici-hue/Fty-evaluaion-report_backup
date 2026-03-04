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
    }
    /* 卡片样式 */
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    /* 按钮样式 */
    .stButton>button {
        border-radius: 8px;
        height: 38px;
        font-weight: 500;
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
                    "版本控制与追溯性": {
                        "total_score": 3,
                        "items": [
                            {"id": "p2_1", "name": "纸样版本控制系统（确保最新、准确、可追溯）", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "p2_2", "name": "文档记录：纸样历史、修订、批准", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "p2_3", "name": "物理纸样及数字备份的安全存储", "score": 1, "is_key": False, "details": [], "comment": ""},
                        ]
                    },
                    "初版审核与文档化": {
                        "total_score": 5,
                        "items": [
                            {"id": "p3_1", "name": "尺寸与工艺审核，应符合技术包要求（检验记录）", "score": 2, "is_key": True, "details": [], "comment": "尺寸审核可提前发现问题，避免批量生产错误"},
                            {"id": "p3_2", "name": "面辅料核对，并按要求进行功能性检测（检验记录）", "score": 3, "is_key": True, "details": [], "comment": "面辅料检测可确保产品品质符合标准"},
                        ]
                    }
                }
            },

            # 2. 面辅料品质控制 (34分)
            "面辅料品质控制": {
                "total_score": 34,
                "sub_modules": {
                    "面料仓库检查": {
                        "total_score": 5,
                        "items": [
                            {
                                "id": "m1_1",
                                "name": "合格/不合格品/待检标识应明确，分开堆放",
                                "score": 1,
                                "is_key": False,
                                "details": ["标识不明确", "未分开堆放"],
                                "comment": ""
                            },
                            {
                                "id": "m1_2",
                                "name": "面料不可“井”字堆放，高度不可过高（建议<1.5m）",
                                "score": 1,
                                "is_key": False,
                                "details": ["面料井字堆放", "堆放高度过高"],
                                "comment": ""
                            },
                            {
                                "id": "m1_3",
                                "name": "不同颜色及批次（缸号）分开堆放",
                                "score": 1,
                                "is_key": False,
                                "details": [],
                                "comment": ""
                            },
                            {
                                "id": "m1_4",
                                "name": "托盘存放不靠墙、不靠窗、避光储存及防潮防霉",
                                "score": 1,
                                "is_key": False,
                                "details": ["靠墙", "靠窗", "未避光储存", "未防潮防霉"],
                                "comment": ""
                            },
                            {
                                "id": "m1_5",
                                "name": "温湿度计及记录（湿度<65%）",
                                "score": 1,
                                "is_key": False,
                                "details": ["无温湿度计", "无记录", "湿度超标"],
                                "comment": "监控湿度的变化，便于采取相应的解决方案（如抽湿）"
                            },
                        ]
                    },
                    "面料入库记录": {
                        "total_score": 2,
                        "items": [
                            {
                                "id": "m2_1",
                                "name": "面料厂验布记录/测试记录/缸差布",
                                "score": 1,
                                "is_key": False,
                                "details": ["无验布记录", "无测试记录", "无缸差布"],
                                "comment": "测试记录和缸差布可预防面料品质问题和色差问题"
                            },
                            {
                                "id": "m2_2",
                                "name": "入库单（卷数，米数，克重等）",
                                "score": 1,
                                "is_key": False,
                                "details": ["无入库单", "信息不全"],
                                "comment": ""
                            },
                        ]
                    },
                    "辅料品质控制": {
                        "total_score": 15,
                        "items": [
                            {"id": "m3_1", "name": "辅料采购符合环保要求（有检测报告）", "score": 2, "is_key": True, "details": ["无检测报告", "不符合环保要求"], "comment": "环保检测可确保产品符合出口标准"},
                            {"id": "m3_2", "name": "辅料储存条件符合要求（防潮、防霉、防蛀）", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "m3_3", "name": "辅料批次管理可追溯", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "m3_4", "name": "拉链、纽扣等功能性测试记录完整", "score": 3, "is_key": True, "details": ["无测试记录", "测试项目不全"], "comment": "功能性测试可确保辅料耐用性"},
                            {"id": "m3_5", "name": "印花/绣花打样确认流程规范", "score": 3, "is_key": True, "details": [], "comment": ""},
                            {"id": "m3_6", "name": "洗水标/吊牌内容符合客户要求", "score": 2, "is_key": True, "details": ["信息错误", "材质不符"], "comment": ""},
                            {"id": "m3_7", "name": "包装辅料（胶袋、纸箱）符合环保标准", "score": 3, "is_key": True, "details": [], "comment": "环保包装是出口产品的基本要求"},
                        ]
                    },
                    "面料检验": {
                        "total_score": 12,
                        "items": [
                            {"id": "m4_1", "name": "面料克重、幅宽抽检记录完整", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "m4_2", "name": "色牢度测试（水洗、摩擦、日晒）", "score": 3, "is_key": True, "details": ["未测试", "测试结果不达标"], "comment": "色牢度是面料品质的核心指标"},
                            {"id": "m4_3", "name": "缩水率测试记录", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "m4_4", "name": "外观检验（破洞、跳纱、污渍）", "score": 2, "is_key": False, "details": [], "comment": ""},
                            {"id": "m4_5", "name": "面料功能性测试（防水、透气等）", "score": 3, "is_key": True, "details": [], "comment": "功能性测试确保产品符合设计要求"},
                        ]
                    }
                }
            },

            # 3. 产前会议 (10分)
            "产前会议": {
                "total_score": 10,
                "sub_modules": {
                    "会议组织": {
                        "total_score": 4,
                        "items": [
                            {"id": "c1_1", "name": "产前会议参会人员齐全（技术、生产、品管）", "score": 2, "is_key": True, "details": [], "comment": "全员参与可确保信息传递准确"},
                            {"id": "c1_2", "name": "会议记录完整并签字确认", "score": 2, "is_key": True, "details": [], "comment": ""},
                        ]
                    },
                    "技术交底": {
                        "total_score": 6,
                        "items": [
                            {"id": "c2_1", "name": "工艺难点提前识别并制定解决方案", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "c2_2", "name": "客户特殊要求传达至所有相关人员", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "c2_3", "name": "首件确认标准明确", "score": 2, "is_key": True, "details": [], "comment": ""},
                        ]
                    }
                }
            },

            # 4. 裁剪 (25分)
            "裁剪": {
                "total_score": 25,
                "sub_modules": {
                    "排料与唛架": {
                        "total_score": 8,
                        "items": [
                            {"id": "cut1_1", "name": "唛架制作优化（提高面料利用率）", "score": 2, "is_key": False, "details": [], "comment": ""},
                            {"id": "cut1_2", "name": "唛架经审核批准后使用", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "cut1_3", "name": "不同尺码、颜色分开排料", "score": 2, "is_key": False, "details": [], "comment": ""},
                            {"id": "cut1_4", "name": "布纹方向符合工艺要求", "score": 2, "is_key": True, "details": [], "comment": ""},
                        ]
                    },
                    "裁剪操作": {
                        "total_score": 9,
                        "items": [
                            {"id": "cut2_1", "name": "面料松布时间符合要求（至少24小时）", "score": 2, "is_key": True, "details": [], "comment": "松布可减少面料张力，降低缩水率"},
                            {"id": "cut2_2", "name": "裁剪精度控制（误差±0.5cm）", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "cut2_3", "name": "裁片数量核对准确", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "cut2_4", "name": "裁片标识清晰（款号、尺码、颜色、裁片名称）", "score": 2, "is_key": True, "details": ["标识缺失", "信息错误"], "comment": ""},
                            {"id": "cut2_5", "name": "刀口、定位孔位置准确", "score": 2, "is_key": False, "details": [], "comment": ""},
                        ]
                    },
                    "裁片管理": {
                        "total_score": 8,
                        "items": [
                            {"id": "cut3_1", "name": "裁片分类堆放，防止混淆", "score": 2, "is_key": False, "details": [], "comment": ""},
                            {"id": "cut3_2", "name": "裁片检验（疵点、色差）", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "cut3_3", "name": "裁片送车间交接记录完整", "score": 2, "is_key": False, "details": [], "comment": ""},
                            {"id": "cut3_4", "name": "余料管理规范（标识、储存）", "score": 2, "is_key": False, "details": [], "comment": ""},
                        ]
                    }
                }
            },

            # 5. 缝制 (35分)
            "缝制": {
                "total_score": 35,
                "sub_modules": {
                    "工序安排": {
                        "total_score": 8,
                        "items": [
                            {"id": "sew1_1", "name": "工序流程图清晰并严格执行", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "sew1_2", "name": "员工技能与工序匹配", "score": 2, "is_key": False, "details": [], "comment": ""},
                            {"id": "sew1_3", "name": "瓶颈工序识别并优化", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "sew1_4", "name": "生产线平衡率≥85%", "score": 2, "is_key": True, "details": [], "comment": "生产线平衡可提高整体效率"},
                        ]
                    },
                    "缝制工艺": {
                        "total_score": 15,
                        "items": [
                            {"id": "sew2_1", "name": "针距密度符合工艺要求（平车12-14针/3cm）", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "sew2_2", "name": "线迹平整，无跳线、浮线、断线", "score": 2, "is_key": True, "details": ["跳线", "浮线", "断线"], "comment": ""},
                            {"id": "sew2_3", "name": "缝份大小均匀一致", "score": 2, "is_key": False, "details": [], "comment": ""},
                            {"id": "sew2_4", "name": "止口顺直，无起皱、扭曲", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "sew2_5", "name": "袋位、扣位、袖笼等关键部位定位准确", "score": 3, "is_key": True, "details": [], "comment": "关键部位定位直接影响产品版型"},
                            {"id": "sew2_6", "name": "锁边/包边工艺符合要求", "score": 2, "is_key": False, "details": [], "comment": ""},
                            {"id": "sew2_7", "name": "打结、回针牢固（起止针处）", "score": 2, "is_key": True, "details": [], "comment": ""},
                        ]
                    },
                    "质量控制": {
                        "total_score": 12,
                        "items": [
                            {"id": "sew3_1", "name": "首件确认制度执行到位", "score": 3, "is_key": True, "details": [], "comment": "首件确认可提前发现工艺问题"},
                            {"id": "sew3_2", "name": "巡检频次合理（每2小时/次）", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "sew3_3", "name": "返修品标识、记录、重检流程规范", "score": 2, "is_key": False, "details": [], "comment": ""},
                            {"id": "sew3_4", "name": "成品尺寸抽检（关键尺寸）", "score": 3, "is_key": True, "details": [], "comment": ""},
                            {"id": "sew3_5", "name": "员工自检、互检制度落实", "score": 2, "is_key": False, "details": [], "comment": ""},
                        ]
                    }
                }
            },

            # 6. 后整 (25分)
            "后整": {
                "total_score": 25,
                "sub_modules": {
                    "整烫": {
                        "total_score": 8,
                        "items": [
                            {"id": "fin1_1", "name": "整烫温度、压力、时间符合面料要求", "score": 2, "is_key": True, "details": [], "comment": "合适的整烫参数可避免面料损伤"},
                            {"id": "fin1_2", "name": "成品定型效果良好（无烫痕、极光）", "score": 2, "is_key": True, "details": ["有烫痕", "有极光"], "comment": ""},
                            {"id": "fin1_3", "name": "整烫后尺寸符合规格", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "fin1_4", "name": "蒸汽品质符合要求（无杂质）", "score": 2, "is_key": False, "details": [], "comment": ""},
                        ]
                    },
                    "检验": {
                        "total_score": 9,
                        "items": [
                            {"id": "fin2_1", "name": "终检标准明确并培训到位", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "fin2_2", "name": "检验项目完整（外观、尺寸、工艺、功能）", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "fin2_3", "name": "检验记录完整可追溯", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "fin2_4", "name": "AQL抽样标准执行到位", "score": 2, "is_key": True, "details": [], "comment": "AQL标准是行业通用的检验规范"},
                            {"id": "fin2_5", "name": "不合格品处理流程规范", "score": 2, "is_key": True, "details": [], "comment": ""},
                        ]
                    },
                    "包装": {
                        "total_score": 8,
                        "items": [
                            {"id": "fin3_1", "name": "包装材料符合客户要求", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "fin3_2", "name": "折叠方式统一规范", "score": 1, "is_key": False, "details": [], "comment": ""},
                            {"id": "fin3_3", "name": "吊牌、洗水标、价格牌位置准确", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "fin3_4", "name": "装箱单与实物一致", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "fin3_5", "name": "外箱标识清晰完整（款号、数量、尺码、目的地）", "score": 1, "is_key": False, "details": [], "comment": ""},
                        ]
                    }
                }
            },

            # 7. 设备管理 (15分)
            "设备管理": {
                "total_score": 15,
                "sub_modules": {
                    "设备维护": {
                        "total_score": 8,
                        "items": [
                            {"id": "eq1_1", "name": "设备保养计划完整并执行", "score": 2, "is_key": True, "details": [], "comment": "定期保养可延长设备寿命"},
                            {"id": "eq1_2", "name": "保养记录完整可追溯", "score": 2, "is_key": False, "details": [], "comment": ""},
                            {"id": "eq1_3", "name": "设备故障维修及时（响应时间<2小时）", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "eq1_4", "name": "备品备件库存充足", "score": 2, "is_key": False, "details": [], "comment": ""},
                        ]
                    },
                    "设备精度": {
                        "total_score": 7,
                        "items": [
                            {"id": "eq2_1", "name": "缝纫机针距、压脚压力定期校准", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "eq2_2", "name": "裁剪机精度校准（每月1次）", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "eq2_3", "name": "整烫设备温度校准", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "eq2_4", "name": "检测仪器校准证书有效", "score": 1, "is_key": False, "details": [], "comment": ""},
                        ]
                    }
                }
            },

            # 8. 质量管理体系 (14分)
            "质量管理体系": {
                "total_score": 14,
                "sub_modules": {
                    "文件体系": {
                        "total_score": 6,
                        "items": [
                            {"id": "qm1_1", "name": "质量手册、程序文件完整有效", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "qm1_2", "name": "作业指导书现场可获取", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "qm1_3", "name": "文件版本控制规范", "score": 2, "is_key": False, "details": [], "comment": ""},
                        ]
                    },
                    "持续改进": {
                        "total_score": 8,
                        "items": [
                            {"id": "qm2_1", "name": "客户投诉处理及时（24小时响应）", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "qm2_2", "name": "内部质量审核定期开展（每季度1次）", "score": 2, "is_key": True, "details": [], "comment": ""},
                            {"id": "qm2_3", "name": "纠正预防措施有效实施", "score": 2, "is_key": True, "details": [], "comment": "纠正预防可避免同类问题重复发生"},
                            {"id": "qm2_4", "name": "质量目标达成率分析与改进", "score": 2, "is_key": True, "details": [], "comment": ""},
                        ]
                    }
                }
            }
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

# ==================== 初始化 ====================
db = DataStore()

# ==================== PDF生成工具 ====================
def generate_pdf(evaluation):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # 标题与基础信息
    elements.append(Paragraph("工厂流程审核报告", styles['Heading1']))
    factory_name = next(f['name'] for f in db.factories if f['id'] == evaluation['factory_id'])
    elements.extend([
        Paragraph(f"工厂名称：{factory_name}", styles['Normal']),
        Paragraph(f"评估日期：{evaluation['eval_date']}", styles['Normal']),
        Paragraph(f"评估人员：{evaluation['evaluator']}", styles['Normal']),
        Paragraph(f"评估类型：{evaluation['eval_type']}", styles['Normal']),
        Paragraph(f"整体评分占比：{evaluation['overall_percent']:.2f}%", styles['Normal']),
        Spacer(1, 12)
    ])

    # 问题汇总
    elements.append(Paragraph("一、存在问题汇总", styles['Heading2']))
    
    # 重点工序问题
    elements.append(Paragraph("1. 重点工序问题", styles['Heading3']))
    has_key_issues = False
    for mod_name in evaluation['selected_modules']:
        mod = db.modules[mod_name]
        for sub_name, sub_mod in mod['sub_modules'].items():
            for item in sub_mod['items']:
                res = evaluation['results'].get(item['id'], {})
                if not res.get('is_checked', False) and item.get('is_key', False):
                    has_key_issues = True
                    elements.append(Paragraph(f"【{mod_name}-{sub_name}】{item['name']}", styles['Normal']))
                    if res.get('details'):
                        elements.append(Paragraph(f"问题详情：{', '.join(res['details'])}", styles['Normal']))
                    if item['comment']:
                        elements.append(Paragraph(f"改进建议：{item['comment']}", styles['Normal']))
                    elements.append(Spacer(1, 6))
    if not has_key_issues:
        elements.append(Paragraph("无重点工序问题", styles['Normal']))
    elements.append(Spacer(1, 12))

    # 其他工序问题
    elements.append(Paragraph("2. 其他工序问题", styles['Heading3']))
    has_other_issues = False
    for mod_name in evaluation['selected_modules']:
        mod = db.modules[mod_name]
        for sub_name, sub_mod in mod['sub_modules'].items():
            for item in sub_mod['items']:
                res = evaluation['results'].get(item['id'], {})
                if not res.get('is_checked', False) and not item.get('is_key', False):
                    has_other_issues = True
                    elements.append(Paragraph(f"【{mod_name}-{sub_name}】{item['name']}", styles['Normal']))
                    if res.get('details'):
                        elements.append(Paragraph(f"问题详情：{', '.join(res['details'])}", styles['Normal']))
                    if item['comment']:
                        elements.append(Paragraph(f"改进建议：{item['comment']}", styles['Normal']))
                    elements.append(Spacer(1, 6))
    if not has_other_issues:
        elements.append(Paragraph("无其他工序问题", styles['Normal']))
    elements.append(Spacer(1, 12))

    # 评估评论
    elements.append(Paragraph("二、评估者评论", styles['Heading2']))
    elements.append(Paragraph(evaluation['comments'] if evaluation['comments'] else "无", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==================== 页面路由 ====================
def main():
    # 登录页 - 现代感设计
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

    # 主界面侧边栏 - 现代感设计
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

# ==================== 核心评估页面 (现代感UI) ====================
def start_evaluation():
    st.markdown("<h2 style='margin-bottom: 20px;'>开始评估</h2>", unsafe_allow_html=True)
    
    # 1. 评估基本信息 - 卡片式布局
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

    # 2. 选择评估大项
    all_modules = list(db.modules.keys())
    if eval_type == "常规审核":
        selected_modules = all_modules
        st.caption("💡 常规审核：默认包含所有8个评估模块")
    else:
        selected_modules = st.multiselect(
            "选择整改模块", 
            all_modules, 
            placeholder="请选择需要复查的模块",
            max_selections=8
        )
        if not selected_modules:
            st.warning("请至少选择一个评估模块")
            st.markdown("</div>", unsafe_allow_html=True)
            return
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. 初始化评估结果存储
    if 'eval_results' not in st.session_state:
        st.session_state.eval_results = {}
        # 预加载所有项为未勾选
        for mod in selected_modules:
            for sub_mod in db.modules[mod]['sub_modules'].values():
                for item in sub_mod['items']:
                    st.session_state.eval_results[item['id']] = {"is_checked": False, "details": []}

    # 4. 评分详情 - 现代感布局
    st.markdown("<h2 style='margin: 20px 0;'>评分详情</h2>", unsafe_allow_html=True)
    total_earned = 0

    for mod_name in selected_modules:
        mod = db.modules[mod_name]
        mod_earned = 0
        
        with st.expander(f"📦 {mod_name}", expanded=True):
            for sub_name, sub_mod in mod['sub_modules'].items():
                # 小项标题：计算小项得分/总分177的百分比
                sub_earned = sum(
                    item['score'] for item in sub_mod['items']
                    if st.session_state.eval_results[item['id']]['is_checked']
                )
                sub_percent = (sub_earned / db.total_system_score * 100) if db.total_system_score > 0 else 0
                
                # 现代感小项标题
                st.markdown(f"### {sub_name} ({sub_percent:.2f}%)", unsafe_allow_html=True)
                st.divider()

                # 遍历每个检查项
                for item in sub_mod['items']:
                    item_id = item['id']
                    # 重点项橙色显示
                    item_label = item['name']
                    if item.get('is_key', False):
                        item_label = f"<span class='orange-text'>{item_label}</span>"
                    
                    # 勾选框：现代感样式
                    is_checked = st.checkbox(
                        item_label,
                        key=f"chk_{item_id}",
                        value=st.session_state.eval_results[item_id]['is_checked'],
                        help=item['comment'] if item['comment'] else None
                    )
                    
                    # 实时更新状态
                    st.session_state.eval_results[item_id]['is_checked'] = is_checked
                    mod_earned += item['score'] if is_checked else 0

                    # 细化选项和Comment放在勾选框正下方
                    if not is_checked:
                        col_detail, col_comment = st.columns([1, 2])
                        with col_detail:
                            # 问题详情选择框
                            if item['details']:
                                details = st.multiselect(
                                    "🔍 问题详情",
                                    item['details'],
                                    key=f"det_{item_id}",
                                    default=st.session_state.eval_results[item_id]['details'],
                                    placeholder="请选择具体问题"
                                )
                                st.session_state.eval_results[item_id]['details'] = details
                        with col_comment:
                            # 自动显示的改进建议
                            if item['comment']:
                                st.info(f"💡 改进建议：{item['comment']}")
                    
                    # 每个检查项之间增加间距
                    st.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)

        total_earned += mod_earned

    # 5. 评估总结与评论 - 卡片式布局
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("### 评估总结", unsafe_allow_html=True)
    
    overall_percent = (total_earned / db.total_system_score * 100) if db.total_system_score > 0 else 0
    # 现代感指标显示
    col_metric, col_comment = st.columns([1, 3])
    with col_metric:
        st.metric(
            label="整体评分占比",
            value=f"{overall_percent:.2f}%",
            delta=f"{overall_percent - 100:.2f}%" if overall_percent < 100 else "+0.00%",
            delta_color="inverse" if overall_percent < 80 else "normal"
        )
    with col_comment:
        comments = st.text_area(
            "评估评论", 
            height=100, 
            placeholder="请输入本次评估的总体评价、整改要求或其他说明...",
            help="此处填写的内容将出现在PDF报告中"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # 6. 保存与生成报告 - 现代感按钮
    col_save, col_reset = st.columns([1, 4])
    with col_save:
        if st.button("💾 保存并生成报告", type="primary", use_container_width=True):
            if not evaluator.strip():
                st.error("请填写评估人员姓名")
                return
                
            evaluation_data = {
                "factory_id": factory_id,
                "evaluator": evaluator,
                "eval_date": eval_date.strftime('%Y-%m-%d'),
                "eval_type": eval_type,
                "selected_modules": selected_modules,
                "overall_percent": overall_percent,
                "results": st.session_state.eval_results,
                "comments": comments
            }
            saved_ev = db.add_evaluation(evaluation_data)
            st.success("✅ 评估记录已保存！")
            
            # 生成PDF并提供下载
            pdf_buffer = generate_pdf(saved_ev)
            st.download_button(
                label="📄 下载PDF报告",
                data=pdf_buffer,
                file_name=f"工厂评估报告_{saved_ev['id']}_{eval_date}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # 重置session
            del st.session_state.eval_results

# ==================== 历史记录页面 (现代感UI) ====================
def show_history():
    st.markdown("<h2 style='margin-bottom: 20px;'>历史记录</h2>", unsafe_allow_html=True)
    
    # 筛选条件
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        factory_filter = st.selectbox("筛选工厂", ["全部"] + [f['name'] for f in db.factories])
    with col2:
        start_date = st.date_input("开始日期", date.today().replace(day=1))
    with col3:
        end_date = st.date_input("结束日期", date.today())
    st.markdown("</div>", unsafe_allow_html=True)

    # 筛选记录
    filtered_evals = []
    for ev in db.evaluations:
        factory_name = next(f['name'] for f in db.factories if f['id'] == ev['factory_id'])
        ev_date = datetime.strptime(ev['eval_date'], '%Y-%m-%d').date()
        
        if (factory_filter == "全部" or factory_name == factory_filter) and \
           (start_date <= ev_date <= end_date):
            filtered_evals.append(ev)

    # 显示记录
    if filtered_evals:
        for ev in reversed(filtered_evals):
            factory_name = next(f['name'] for f in db.factories if f['id'] == ev['factory_id'])
            
            # 现代感展开框
            with st.expander(f"📅 {ev['eval_date']} | 🏭 {factory_name} | 📝 {ev['eval_type']}", expanded=False):
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns([2,2,2,1])
                with col1: st.write(f"**评估人**：{ev['evaluator']}")
                with col2: st.write(f"**创建时间**：{ev['created_at']}")
                with col3: 
                    # 评分占比颜色区分
                    percent = float(ev['overall_percent'])
                    color = "#10b981" if percent >= 80 else "#f59e0b" if percent >= 60 else "#ef4444"
                    st.write(f"**整体评分占比**：<span style='color: {color}; font-weight: 600;'>{percent:.2f}%</span>", unsafe_allow_html=True)
                with col4:
                    pdf_buffer = generate_pdf(ev)
                    st.download_button(
                        "下载报告",
                        data=pdf_buffer,
                        file_name=f"评估报告_{ev['id']}_{ev['eval_date']}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"dl_{ev['id']}"
                    )
                
                # 评论显示
                if ev['comments']:
                    st.markdown("**评估评论**：")
                    st.write(ev['comments'])
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='metric-card'><p style='text-align: center; color: #64748b; padding: 20px;'>暂无符合条件的评估记录</p></div>", unsafe_allow_html=True)

# ==================== 对比分析页面 (基础框架) ====================
def show_comparison():
    st.markdown("<h2 style='margin-bottom: 20px;'>对比分析</h2>", unsafe_allow_html=True)
    st.markdown("<div class='metric-card'><p style='text-align: center; color: #64748b; padding: 40px;'>📊 对比分析功能开发中，即将上线...</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
