# -*- coding: utf-8 -*-
"""
文匠 Word 模板对比测试运行脚本
"""

import os
from wenjiang import Converter

# 定义测试输入与输出文件名
source_file = "test_code_blocks.md"
output_default = "output_default.docx"
output_custom = "output_custom.docx"

# 检查输入测试文件是否存在
if not os.path.exists(source_file):
    print(f"错误: 找不到测试源文件 {source_file}")
    exit(1)

# ==============================================================================
# 方案 1：仅使用默认模板 office_basic.docx
# ==============================================================================
print("正在执行方案 1: 仅使用默认模板 (office_basic.docx)...")
try:
    # 默认模板不带 custom 代码块样式定义，通常退化为系统底色和常规段落
    converter_default = Converter(template="templates/office_basic.docx")
    
    result_default = converter_default.convert(
        source_file=source_file,
        output_file=output_default
    )
    print(f"方案 1 转换成功! 生成文件: {output_default}")
    print(f"转换结果返回值: {result_default}\n")
except Exception as e:
    print(f"方案 1 转换失败: {e}\n")


# ==============================================================================
# 方案 2：加载精调代码模板 WenJiangCode.docx
# ==============================================================================
print("正在执行方案 2: 使用精调代码模板 (WenJiangCode.docx)...")
try:
    # 自定义模板内部定义了 SourceCode 段落样式和 Consolas 字体
    converter_custom = Converter(template="templates/WenJiangCode.docx")
    
    result_custom = converter_custom.convert(
        source_file=source_file,
        output_file=output_custom
    )
    print(f"方案 2 转换成功! 生成文件: {output_custom}")
    print(f"转换结果返回值: {result_custom}\n")
except Exception as e:
    print(f"方案 2 转换失败: {e}\n")

print("测试完成！请在当前目录下打开以下两个文档对比排版效果：")
print(f"1. 默认模板渲染效果: {os.path.abspath(output_default)}")
print(f"2. 精调模板渲染效果: {os.path.abspath(output_custom)}")
