from fastapi import FastAPI, UploadFile, File
import pandas as pd
import tempfile

app = FastAPI(title="Excel 分析 API", version="1.0")


@app.get("/")
def root():
    return {"message": "Excel 分析 API 已启动，上传 Excel 文件进行分析"}


@app.post("/analyze-excel")
async def analyze_excel(file: UploadFile = File(...)):
    # 保存上传的文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # 读取并分析
    df = pd.read_excel(tmp_path)

    result = {
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "summary": {}
    }

    # 对数值列做统计
    for col in df.select_dtypes(include=['number']).columns:
        result["summary"][col] = {
            "mean": round(df[col].mean(), 2),
            "max": float(df[col].max()),
            "min": float(df[col].min())
        }

    return result