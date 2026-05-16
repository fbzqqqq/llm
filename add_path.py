"""
在每个Notebook开头添加 sys.path 以导入 d2l_compat
如果已有 from d2l_compat import *，则在前面添加 sys.path
"""
import json
import os


def add_path_to_notebook(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    modified = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue

        source = cell.get('source', [])
        if not source:
            continue

        source_str = ''.join(source)

        # 如果已经有 sys.path + d2l_compat，跳过
        if 'sys.path' in source_str and 'd2l_compat' in source_str:
            continue

        # 如果只有 from d2l_compat import *，在前面加 sys.path
        if 'from d2l_compat import *' in source_str:
            new_source = ['import sys\n', "sys.path.insert(0, '..')\n"] + source
            cell['source'] = new_source
            modified = True
            break  # 只处理第一个匹配的

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
                if add_path_to_notebook(path):
                    count += 1
                    print(f"[ADDED] {path}")

    print(f"\n修改了 {count} 个文件")


if __name__ == '__main__':
    main()
