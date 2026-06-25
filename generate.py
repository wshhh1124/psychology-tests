#!/usr/bin/env python3
"""
心理测试网页生成器
用法: python3 generate.py <config.json> [output.html]

给定一个测试配置JSON，将模板中的 TEST_CONFIG 替换为实际配置，
输出一个独立的、可直接部署的HTML文件。
"""
import json
import sys
import os

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'template.html')

def generate(config_path, output_path=None):
    # Read config
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Read template
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    # Find and replace TEST_CONFIG
    marker_start = 'const TEST_CONFIG = {'
    marker_start_idx = template.find(marker_start)
    if marker_start_idx == -1:
        print('❌ 错误: 模板中找不到 TEST_CONFIG')
        sys.exit(1)

    # Find the matching closing brace for the TEST_CONFIG object
    # We do this by finding the "};" after "const TEST_CONFIG = {"
    # Find the end of the config object by tracking braces
    brace_count = 0
    in_config = False
    config_start = marker_start_idx + len('const TEST_CONFIG =')
    config_end = None

    for i in range(config_start, len(template)):
        ch = template[i]
        if ch == '{':
            brace_count += 1
            in_config = True
        elif ch == '}':
            brace_count -= 1
            if in_config and brace_count == 0:
                # Check if next non-whitespace char is ';'
                j = i + 1
                while j < len(template) and template[j] in ' \t':
                    j += 1
                if j < len(template) and template[j] == ';':
                    config_end = j + 1
                else:
                    config_end = i + 1
                break

    if config_end is None:
        print('❌ 错误: 无法定位 TEST_CONFIG 结束位置')
        sys.exit(1)

    before = template[:marker_start_idx]
    after = template[config_end:]

    new_config = 'const TEST_CONFIG = ' + json.dumps(config, ensure_ascii=False, indent=2) + ';'

    output = before + new_config + after

    # Determine output path
    if output_path is None:
        base = os.path.splitext(os.path.basename(config_path))[0]
        output_path = os.path.join(os.path.dirname(__file__), 'docs', f'{base}.html')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f'✅ 生成成功: {output_path}')
    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python3 generate.py <config.json> [output.html]')
        print('示例: python3 generate.py tests/love-style.json docs/love-style.html')
        sys.exit(1)

    config_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    generate(config_file, out_file)
