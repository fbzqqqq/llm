"""
修复Notebook中的换行符问题，并添加sys.path以导入d2l_compat
"""
import json
import os


def fix_notebook(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    modified = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue

        source = cell.get('source', [])
        if not source:
            continue

        # 如果是字符串列表
        if isinstance(source, list):
            # 先join成完整字符串
            source_str = ''.join(source)
            # 重新分行，每行保留换行符（除了最后一行）
            lines = source_str.split('\n')
            new_source = []
            for i, line in enumerate(lines):
                if i < len(lines) - 1:
                    new_source.append(line + '\n')
                elif line:
                    new_source.append(line)

            if new_source != source:
                cell['source'] = new_source
                modified = True

    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)

    return modified


def main():
    base = 'notebooks'
    count = 0
    for root, dirs, files in os.walk(base):
        for fname in files:
            if fname.endswith('.ipynb'):
                path = os.path.join(root, fname)
                if fix_notebook(path):
                    count += 1
                    print(f"[FIXED] {path}")
                else:
                    print(f"[OK] {path}")

    print(f"\n修复了 {count} 个文件")


if __name__ == '__main__':
    main()
