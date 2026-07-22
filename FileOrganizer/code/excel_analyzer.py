"""
Excel 数据分析 + AI 报告生成器
功能：输入一个成绩/销售Excel，自动生成统计结果 + 自然语言总结
售价参考：300~500元
"""

import pandas as pd
from pathlib import Path
from openai import OpenAI
import os

# 配置 API（从环境变量读取，更安全）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    # 如果还没配环境变量，在这里临时填一下（用完记得删）
    DEEPSEEK_API_KEY = "你的API"  # 测试完立刻换成环境变量方式！

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


def analyze_excel(file_path: str):
    """
    核心函数：读取Excel → 计算统计指标 → 调用AI生成总结
    """
    # 1. 读取Excel
    df = pd.read_excel(file_path)
    print(f"📊 成功读取数据，共 {len(df)} 行，{len(df.columns)} 列")
    print(f"列名：{df.columns.tolist()}")

    # 2. 自动检测数值列并计算统计信息
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        print("❌ 没有找到数值列，请检查Excel内容")
        return

    print(f"📈 检测到数值列：{numeric_cols}")

    # 3. 构建统计报告（用字典存，方便传给AI）
    stats = {}
    for col in numeric_cols:
        stats[col] = {
            '平均值': df[col].mean(),
            '最大值': df[col].max(),
            '最小值': df[col].min(),
            '总和': df[col].sum(),
            '计数': df[col].count()
        }

    # 4. 把统计结果转成文本，给AI看
    stats_text = ""
    for col, values in stats.items():
        stats_text += f"- {col}: 平均{values['平均值']:.2f}, 最大{values['最大值']}, 最小{values['最小值']}, 总计{values['总和']:.2f}\n"

    # 5. 调用AI生成业务洞察（这是你的溢价点）
    print("🤖 AI正在生成分析报告...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个数据分析专家，请根据提供的统计信息，用中文写一段简洁的业务洞察报告（200字以内），指出亮点和问题。"},
                {"role": "user", "content": f"以下是某数据的统计结果：\n{stats_text}"}
            ],
            temperature=0.7,
        )
        ai_summary = response.choices[0].message.content
    except Exception as e:
        ai_summary = f"AI生成失败，请检查API密钥：{e}"

    # 6. 输出完整报告（控制台 + 保存为文本文件）
    report = f"""
========================================
Excel 数据分析报告
========================================
数据概况：共 {len(df)} 行，{len(df.columns)} 列

统计摘要：
{stats_text}

AI 洞察：
{ai_summary}
========================================
    """
    print(report)

    # 7. 保存报告到文件（客户需要的是“交付物”）
    output_path = Path(file_path).parent / f"{Path(file_path).stem}_分析报告.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ 报告已保存至：{output_path}")


# 启动入口
if __name__ == "__main__":
    # 找一个你电脑里的Excel文件测试（如果没测试文件，先跳过）
    file_path = input("请输入Excel文件路径（例如：./test_data/成绩表.xlsx）: ").strip()
    if not Path(file_path).exists():
        print("❌ 文件不存在，请检查路径")
    else:
        analyze_excel(file_path)