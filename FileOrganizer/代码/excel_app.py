"""
AI Excel 分析助手 - 增强版（带图表）

"""
import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载 .env 文件里的密钥
load_dotenv()

st.set_page_config(page_title="AI 数据分析专家", page_icon="📊")
st.title("📊 AI 智能 Excel 分析助手")
st.caption("上传 Excel，AI 自动生成统计报告 + 可视化图表 + 业务洞察")

# 从环境变量读取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    st.error("⚠️ 请在项目根目录创建 .env 文件，并写入 DEEPSEEK_API_KEY=你的密钥")
    st.stop()

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

uploaded_file = st.file_uploader("📁 上传 Excel 文件 (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ 读取成功！共 {len(df)} 行，{len(df.columns)} 列")

    with st.expander("👀 点击查看原始数据"):
        st.dataframe(df)

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        st.warning("未检测到数值列")
        st.stop()

    # 选择要可视化的列
    col_to_plot = st.selectbox("📈 选择要可视化的指标", numeric_cols)

    if st.button("🚀 生成完整分析报告", type="primary"):
        with st.spinner("AI 分析中..."):
            # 1. 统计计算
            stats = {}
            for col in numeric_cols:
                stats[col] = {
                    '平均值': df[col].mean(),
                    '最大值': df[col].max(),
                    '最小值': df[col].min(),
                    '总和': df[col].sum()
                }

            stats_text = ""
            for col, v in stats.items():
                stats_text += f"- {col}: 平均{v['平均值']:.2f}, 最大{v['最大值']}, 最小{v['最小值']}\n"

            # 2. 调用 AI
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是数据分析专家，请根据统计信息给出 200 字以内的中文洞察，指出亮点与问题。"},
                        {"role": "user", "content": stats_text}
                    ]
                )
                ai_result = response.choices[0].message.content
            except Exception as e:
                ai_result = f"AI 调用失败：{e}"

            # 3. 展示结果（双列布局：左统计，右图表）
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📈 统计摘要")
                st.dataframe(pd.DataFrame(stats))

            with col2:
                st.subheader("📊 数据分布（柱状图）")
                # 画柱状图
                st.bar_chart(df[col_to_plot])

            # 4. AI 洞察（全宽展示）
            st.subheader("🤖 AI 业务洞察")
            st.success(ai_result)

            # 5. 下载按钮
            report_content = f"数据统计:\n{stats_text}\n\nAI洞察:\n{ai_result}"
            st.download_button("📥 下载完整报告", data=report_content, file_name="分析报告.txt")