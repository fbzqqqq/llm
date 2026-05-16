"""
批量重构Notebook脚本：将 d2l 依赖替换为 d2l_compat
"""
import json
import os
import re

# 源目录和目标目录的映射
DIR_MAP = {
    'fundamentals': 'notebooks/fundamentals',
    'mlp': 'notebooks/mlp',
    'cnn': 'notebooks/cnn',
    'computer-vision': 'notebooks/computer-vision',
    'rnn': 'notebooks/rnn',
    'nlp': 'notebooks/nlp',
    'optimization': 'notebooks/optimization',
    'projects': 'notebooks/projects',
}


def replace_d2l_in_code(code: str) -> str:
    """替换代码中的 d2l 导入和调用"""
    if not code.strip():
        return code

    # 1. 替换 d2l 导入语句
    # from d2l import torch as d2l
    code = re.sub(
        r'^from\s+d2l\s+import\s+torch\s+as\s+d2l\s*$',
        'from d2l_compat import *',
        code, flags=re.MULTILINE
    )
    # import d2l
    code = re.sub(
        r'^import\s+d2l\s*$',
        'from d2l_compat import *',
        code, flags=re.MULTILINE
    )
    # from d2l import torch as d2l  # 有注释的情况
    code = re.sub(
        r'^from\s+d2l\s+import\s+torch\s+as\s+d2l.*$',
        'from d2l_compat import *',
        code, flags=re.MULTILINE
    )

    # 2. 替换 d2l. 前缀调用
    # 但需要小心：不要替换字符串中的 d2l.
    # 使用简单的正则：匹配 d2l. 后面跟着一个有效的标识符
    def replace_d2l_prefix(match):
        # 检查是否在字符串中（简单启发式）
        before = code[:match.start()]
        # 数一下前面的引号数量
        single_quotes = before.count("'") - before.count("\\'")
        double_quotes = before.count('"') - before.count('\\"')
        # 如果在一个未闭合的字符串中，不替换
        # 这是一个简化判断，可能有误但大部分情况ok
        return match.group(0)  # 不做替换，让后续步骤处理

    # 更安全的方法：逐行处理，跳过字符串和注释
    lines = code.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.strip()
        # 跳过空行和纯注释行
        if not stripped or stripped.startswith('#'):
            new_lines.append(line)
            continue

        # 替换行中的 d2l.xxx (不在字符串中)
        # 使用更精确的方法：只替换不在引号中的 d2l.
        new_line = replace_d2l_in_line(line)
        new_lines.append(new_line)

    return '\n'.join(new_lines)


def replace_d2l_in_line(line: str) -> str:
    """替换单行中的 d2l. 前缀，避免替换字符串中的"""
    result = []
    i = 0
    in_string = False
    string_char = None
    escaped = False

    while i < len(line):
        char = line[i]

        # 处理转义
        if escaped:
            result.append(char)
            escaped = False
            i += 1
            continue

        if char == '\\':
            result.append(char)
            escaped = True
            i += 1
            continue

        # 处理字符串边界
        if not in_string and char in ('"', "'"):
            in_string = True
            string_char = char
            result.append(char)
            i += 1
            continue
        elif in_string and char == string_char:
            in_string = False
            string_char = None
            result.append(char)
            i += 1
            continue

        # 在字符串中，直接复制
        if in_string:
            result.append(char)
            i += 1
            continue

        # 检查是否是 d2l. 前缀
        if i + 4 <= len(line) and line[i:i+4] == 'd2l.':
            # 确认后面是一个有效的标识符字符
            if i + 4 < len(line) and (line[i+4].isalpha() or line[i+4] == '_'):
                # 替换 d2l. 为空
                i += 4  # 跳过 'd2l.'
                continue

        result.append(char)
        i += 1

    return ''.join(result)


def process_notebook(src_path: str, dst_path: str):
    """处理单个 Notebook 文件"""
    with open(src_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    modified = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            if isinstance(source, list):
                source_str = ''.join(source)
            else:
                source_str = source

            new_source = replace_d2l_in_code(source_str)
            if new_source != source_str:
                # 正确保留换行符：每行末尾加 \n（最后一行除外）
                lines = new_source.split('\n')
                new_lines = []
                for i, line in enumerate(lines):
                    if i < len(lines) - 1:
                        new_lines.append(line + '\n')
                    elif line:
                        new_lines.append(line)
                cell['source'] = new_lines
                modified = True

    # 确保输出目录存在
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    with open(dst_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)

    return modified


def main():
    total = 0
    modified_count = 0

    for src_dir, dst_dir in DIR_MAP.items():
        src_full = os.path.join('.', src_dir)
        if not os.path.exists(src_full):
            print(f"跳过不存在的目录: {src_full}")
            continue

        for fname in os.listdir(src_full):
            if not fname.endswith('.ipynb'):
                continue

            src_path = os.path.join(src_full, fname)
            dst_path = os.path.join(dst_dir, fname)

            print(f"处理: {src_path} -> {dst_path}")
            try:
                modified = process_notebook(src_path, dst_path)
                total += 1
                if modified:
                    modified_count += 1
                    print(f"  [OK] 已修改")
                else:
                    print(f"  [SKIP] 无需修改")
            except Exception as e:
                print(f"  [ERR] 错误: {e}")

    print(f"\n完成: {total} 个文件, {modified_count} 个被修改")


if __name__ == '__main__':
    main()
