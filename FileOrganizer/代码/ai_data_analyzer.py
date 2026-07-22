"""
AI + 爬虫数据自动分析器（完整版）
功能：选择 CSV → AI 生成洞察 → 保存报告
"""
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
import glob
from datetime import datetime

# 加载环境变量
load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def get_csv_file():
    """交互式选择 CSV 文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) != "FileOrganizer" else script_dir
    target_dir = os.path.join(project_root, "数据文件")

    if not os.path.exists(target_dir):
        print(f"❌ 文件夹不存在: {target_dir}")
        return None

    files = glob.glob(os.path.join(target_dir, "*.csv"))
    if not files:
        print(f"❌ 在 {target_dir} 中没有找到 CSV 文件")
        return None

    print("\n📂 找到以下 CSV 文件：")
    for i, file in enumerate(files, 1):
        file_name = os.path.basename(file)
        file_size = os.path.getsize(file) / 1024
        print(f"  {i}. {file_name} ({file_size:.1f} KB)")

    print("\n" + "=" * 40)
    choice = input("请输入文件编号（直接回车则使用最新文件）: ").strip()

    if choice == "":
        selected = max(files, key=os.path.getmtime)
        print(f"✅ 自动选择最新文件: {os.path.basename(selected)}")
        return selected
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                selected = files[idx]
                print(f"✅ 已选择: {os.path.basename(selected)}")
                return selected
            else:
                print(f"❌ 编号 {choice} 无效，使用最新文件")
                selected = max(files, key=os.path.getmtime)
                return selected
        except ValueError:
            print(f"❌ 输入无效，使用最新文件")
            selected = max(files, key=os.path.getmtime)
            return selected

def analyze_data_with_ai(csv_path):
    """读取 CSV，调用 AI 生成洞察"""
    print(f"\n📂 正在分析文件: {os.path.basename(csv_path)}")

    df = pd.read_csv(csv_path)
    print(f"📊 数据概况: {len(df)} 行, {len(df.columns)} 列")
    print(f"列名: {df.columns.tolist()}")

    sample_size = min(50, len(df))
    sample_df = df.head(sample_size)
    data_text = sample_df.to_string(index=False)

    prompt = f"""
你是一位资深数据分析师。请根据以下数据样本（共 {len(df)} 条记录，展示前 {sample_size} 条），用中文写一份 300 字以内的分析报告。

**输出格式要求**：
1. **核心结论**：用200字总结这批数据最显著的特征。
2. **数据佐证**：引用样本中的具体数字或例子来支撑你的结论。
3. **行动建议**：给出 1-2 条具体可执行的建议，100字左右。

**数据样本（CSV 格式）**："""
    print("🤖 AI 正在生成洞察报告...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的数据分析师，擅长从数据中发现商业洞察。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        report = response.choices[0].message.content
        # ★★★ 关键：必须返回两个值 ★★★
        return report, df
    except Exception as e:
        print(f"❌ AI 调用失败: {e}")
        # ★★★ 失败时也返回 None，但主程序会判断 ★★★
        return None, df

def save_report(report, original_csv_path, df):
    """保存报告到 数据文件 文件夹"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) != "FileOrganizer" else script_dir
    target_dir = os.path.join(project_root, "数据文件")
    os.makedirs(target_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(original_csv_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(target_dir, f"{base_name}_分析报告_{timestamp}.txt")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"数据源文件: {os.path.basename(original_csv_path)}\n")
        f.write(f"数据总行数: {len(df)}\n")
        f.write(f"数据列: {', '.join(df.columns)}\n")
        f.write("=" * 50 + "\n")
        f.write(report)

    print(f"✅ 报告已保存: {report_path}")
    return report_path

if __name__ == "__main__":
    print("=" * 40)
    print("📊 AI 数据自动分析器")
    print("=" * 40)

    csv_file = get_csv_file()
    if not csv_file:
        print("❌ 没有找到可用的 CSV 文件。")
        exit()

    report, df = analyze_data_with_ai(csv_file)
    if report:
        save_report(report, csv_file, df)
        print("\n" + "=" * 40)
        print("📈 AI 洞察报告预览:")
        print("=" * 40)
        print(report)
    else:
        print("❌ 分析失败。")
