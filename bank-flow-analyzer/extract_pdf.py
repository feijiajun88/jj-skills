#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF文本提取脚本
"""
from PyPDF2 import PdfReader
import sys

def extract_pdf_text(pdf_path):
    """提取PDF文件中的所有文本"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        total_pages = len(reader.pages)

        print(f"总页数: {total_pages}")
        print("=" * 80)

        for page_num in range(total_pages):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            text += f"\n\n--- 第 {page_num + 1} 页 ---\n"
            text += page_text

        return text
    except Exception as e:
        return f"错误: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 extract_pdf.py <pdf路径> [输出路径]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        output_path = "pdf_extracted_text.txt"

    text = extract_pdf_text(pdf_path)

    # 保存到文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"\n文本已保存到: {output_path}")
    print("=" * 80)

    # 打印前5000字符用于预览
    print("\n前5000字符预览:")
    print(text[:5000])
