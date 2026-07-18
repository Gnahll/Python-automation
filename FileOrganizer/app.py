"""
AI Excel 分析助手 - Web 版
"""
import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv


# ===== 强制指定 .env 路径 =====
env_path = r"D:\Python自动化\FileOrganizer\.env"
load_dotenv(env_path)

# 页面标题和图标
st.set_page_config(page_title="AI 数据分析助手", page_icon="📊")
st.title("📊 AI 智能 Excel 分析助手")
st.caption("上传你的 Excel 文件，AI 自动生成统计报告和业务洞察")

# 获取 API Key（从环境变量读取）
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    st.error("⚠️ 未检测到 API Key，请在终端执行：$env:DEEPSEEK_API_KEY='你的密钥'")
    st.stop()

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 文件上传组件
uploaded_file = st.file_uploader("📁 请上传 Excel 文件 (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # 1. 读取文件
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ 读取成功！共 {len(df)} 行，{len(df.columns)} 列")

    # 显示原始数据预览
    with st.expander("👀 点击查看数据预览"):
        st.dataframe(df)

    # 2. 自动检测数值列
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        st.warning("未检测到数值列，请检查数据格式")
        st.stop()

    # 3. 点击按钮开始分析
    if st.button("🚀 生成 AI 分析报告", type="primary"):
        with st.spinner("AI 正在努力分析中..."):
            # 计算统计
            stats = {}
            for col in numeric_cols:
                stats[col] = {
                    '平均值': df[col].mean(),
                    '最大值': df[col].max(),
                    '最小值': df[col].min(),
                    '总和': df[col].sum()
                }

            # 构建统计文本给 AI
            stats_text = ""
            for col, v in stats.items():
                stats_text += f"- {col}: 平均{v['平均值']:.2f}, 最大{v['最大值']}, 最小{v['最小值']}\n"

            # 调用 AI
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system",
                         "content": "你是数据分析专家，请根据统计信息给出 200 字以内的中文洞察，指出亮点与问题。"},
                        {"role": "user", "content": stats_text}
                    ]
                )
                ai_result = response.choices[0].message.content
            except Exception as e:
                ai_result = f"AI 调用失败：{e}"

            # 显示结果
            st.subheader("📈 统计摘要")
            st.dataframe(pd.DataFrame(stats))

            st.subheader("🤖 AI 业务洞察")
            st.success(ai_result)

            # 提供下载按钮
            report_content = f"数据统计:\n{stats_text}\n\nAI洞察:\n{ai_result}"
            st.download_button(
                label="📥 下载分析报告 (.txt)",
                data=report_content,
                file_name="分析报告.txt",
                mime="text/plain"
            )
