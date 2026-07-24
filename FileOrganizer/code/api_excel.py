from fastapi import FastAPI, UploadFile, File, HTTPException, Query
import pandas as pd
import tempfile
import os
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # 本地开发时读取 .env

app = FastAPI(title="Excel 智能分析 API", version="2.0")

# ---------- AI 客户端配置 ----------
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)


# ---------- 根路径 ----------
@app.get("/")
def root():
    return {"message": "Excel 智能分析 API 已启动"}


# ---------- 基础分析（原有） ----------
@app.post("/analyze-excel")
async def analyze_excel(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx 或 .xls 文件")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    df = pd.read_excel(tmp_path)
    os.unlink(tmp_path)  # 清理临时文件

    result = {
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "summary": {}
    }

    for col in df.select_dtypes(include=["number"]).columns:
        result["summary"][col] = {
            "mean": round(df[col].mean(), 2),
            "max": float(df[col].max()),
            "min": float(df[col].min()),
            "sum": float(df[col].sum())
        }

    return result


# ---------- 高级分析（新增：AI + 图表） ----------
@app.post("/analyze-advanced")
async def analyze_advanced(
        file: UploadFile = File(...),
        chart_col: str = Query(None, description="要生成图表的列名，若不指定则使用第一个数值列")
):
    # 1. 读取 Excel
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx 或 .xls 文件")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    df = pd.read_excel(tmp_path)
    os.unlink(tmp_path)

    # 2. 统计数值列
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        raise HTTPException(status_code=400, detail="未检测到数值列")

    stats = {}
    for col in numeric_cols:
        stats[col] = {
            "mean": round(df[col].mean(), 2),
            "max": float(df[col].max()),
            "min": float(df[col].min()),
            "sum": float(df[col].sum())
        }

    # 3. 选择图表列
    if chart_col and chart_col not in numeric_cols:
        raise HTTPException(status_code=400, detail=f"列 '{chart_col}' 不是数值列")
    plot_col = chart_col if chart_col else numeric_cols[0]

    # 4. 生成图表（返回 base64 图片）
    fig, ax = plt.subplots(figsize=(8, 5))
    df[plot_col].plot(kind="bar", ax=ax)
    ax.set_title(f"分布：{plot_col}")
    ax.set_xlabel("行索引")
    ax.set_ylabel(plot_col)
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")

    # 5. 调用 AI 生成洞察
    ai_text = ""
    try:
        stats_text = "\n".join(
            [f"- {col}: 平均值 {v['mean']}, 最大值 {v['max']}, 最小值 {v['min']}" for col, v in stats.items()])
        prompt = f"""请根据以下统计数据，用中文写一段 100～150 字的业务洞察，指出数据特征、趋势或异常。
数据概况：共 {len(df)} 行，列：{', '.join(df.columns)}
统计如下：
{stats_text}
"""
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        ai_text = response.choices[0].message.content
    except Exception as e:
        ai_text = f"AI 分析调用失败：{str(e)}"

    # 6. 返回最终结果
    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "summary": stats,
        "ai_insight": ai_text,
        "chart": {
            "column": plot_col,
            "image_base64": img_base64  # 前端可直接渲染
        }
    }