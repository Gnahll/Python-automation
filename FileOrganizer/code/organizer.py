import os
import shutil
from pathlib import Path
from openai import OpenAI

# ========================
# 1. 配置你的API Key（先拿免费测试）
# ========================
# 去 DeepSeek 官网注册，充值几块钱够测试很久了
DEEPSEEK_API_KEY = "你的密钥"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# ========================
# 2. 规则引擎（优先判断，省钱又快）
# ========================
KEYWORD_RULES = {
    "论文": ["论文", "毕业设计", "thesis", "开题报告", "参考文献"],
    "报告": ["报告", "汇报", "PPT", "presentation", "总结", "月报"],
    "code": [".py", ".js", ".java", ".c", ".cpp", "源码", "算法"],
    "图片": [".jpg", ".png", ".gif", ".bmp", ".svg", "截图"],
    "财务": ["报销", "工资", "账单", "invoice", "发票", "银行"],
    "合同": ["合同", "协议", "agreement", "契约"]
}

# 扩展名兜底映射（纯规则）
EXTENSION_MAP = {
    ".pdf": "论文",
    ".docx": "报告",
    ".xlsx": "财务",
    ".pptx": "报告",
    ".jpg": "图片",
    ".png": "图片",
    ".zip": "压缩包",
    ".rar": "压缩包",
    ".csv": "数据文件"
}


def rule_based_classify(filename: str) -> str:
    """先用关键词和扩展名进行规则匹配，命中直接返回"""
    file_lower = filename.lower()

    # 检查扩展名
    ext = Path(filename).suffix.lower()
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]

    # 检查关键词
    for category, keywords in KEYWORD_RULES.items():
        for kw in keywords:
            if kw in file_lower:
                return category
    return None  # 规则没命中，交给AI


# ========================
# 3. AI兜底分类器（只有规则认不出的才调用，省钱）
# ========================
def ai_based_classify(filename: str) -> str:
    """调用大模型猜这个文件属于什么类别"""
    print(f"🤖 AI正在分析: {filename}")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system",
                 "content": "你是一个文件分类专家。请根据文件名，只输出一个中文类别词（如：论文、报告、图片、代码、财务、合同、学习资料、其他），不要输出任何解释。"},
                {"role": "user", "content": f"文件名是：{filename}，请分类。"}
            ],
            temperature=0.1,
            max_tokens=10
        )
        category = response.choices[0].message.content.strip()
        # 做个简单的清洗，防止AI抽风输出多余文字
        if len(category) > 6:
            return "其他"
        return category if category else "其他"
    except Exception as e:
        print(f"⚠️ AI调用失败，归入其他: {e}")
        return "其他"


# ========================
# 4. 核心整理函数
# ========================
def organize_folder(target_dir: str):
    """整理指定目录下的所有文件"""
    target_path = Path(target_dir)
    if not target_path.exists():
        print("❌ 目录不存在！")
        return

    # 获取该目录下所有文件（不包括文件夹）
    files = [f for f in target_path.iterdir() if f.is_file()]

    if not files:
        print("📭 该目录下没有文件需要整理。")
        return

    print(f"📂 开始整理: {target_dir}，共 {len(files)} 个文件")

    for file_path in files:
        filename = file_path.name

        # --- 第一步：规则匹配 ---
        category = rule_based_classify(filename)

        # --- 第二步：规则未命中则调AI ---
        if category is None:
            category = ai_based_classify(filename)

        # --- 第三步：构建目标文件夹并移动 ---
        dest_folder = target_path / category
        dest_folder.mkdir(exist_ok=True)  # 不存在则创建

        dest_path = dest_folder / filename

        # 处理重名（若存在则在名字后加编号）
        counter = 1
        while dest_path.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            new_name = f"{stem}_{counter}{suffix}"
            dest_path = dest_folder / new_name
            counter += 1

        # 执行移动
        shutil.move(str(file_path), str(dest_path))
        print(f"✅ {filename} → [{category}]文件夹")

    print("🎉 整理完成！")


# ========================
# 5. 启动入口
# ========================
if __name__ == "__main__":
    # 强烈建议先拿「下载文件夹」试水，请替换成你自己的路径
    # Windows示例: C:/Users/你的用户名/Downloads
    # Mac示例: /Users/你的用户名/Downloads
    TARGET = input("请输入要整理的文件夹路径（直接回车则整理当前目录）: ").strip()
    if not TARGET:
        TARGET = "./test_files"  # 如果没有输入，默认整理当前目录下的 test_files（建议先建个测试文件夹）

    organize_folder(TARGET)