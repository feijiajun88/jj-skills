#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的PDF文本提取脚本 - 支持中文和表格提取
"""
import sys
import pdfplumber
import fitz  # pymupdf
from collections import defaultdict

def extract_with_pdfplumber(pdf_path):
    """使用pdfplumber提取PDF文本（适合表格）"""
    print("使用 pdfplumber 提取...")
    text = ""
    tables = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"总页数: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages):
                text += f"\n\n{'='*80}\n"
                text += f"--- 第 {page_num + 1} 页 ---\n"
                text += f"{'='*80}\n\n"
                
                # 提取文本
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                
                # 提取表格
                page_tables = page.extract_tables()
                if page_tables:
                    text += "\n[表格数据]\n"
                    for i, table in enumerate(page_tables):
                        text += f"\n--- 表格 {i+1} ---\n"
                        for row in table:
                            if row:
                                row_text = " | ".join([str(cell) if cell else "" for cell in row])
                                text += row_text + "\n"
                    tables.extend(page_tables)
        
        return text, tables
    except Exception as e:
        print(f"pdfplumber 提取错误: {e}")
        return "", []

def extract_with_fitz(pdf_path):
    """使用pymupdf提取PDF文本（速度快）"""
    print("使用 pymupdf 提取...")
    text = ""
    
    try:
        doc = fitz.open(pdf_path)
        print(f"总页数: {len(doc)}")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text += f"\n\n{'='*80}\n"
            text += f"--- 第 {page_num + 1} 页 ---\n"
            text += f"{'='*80}\n\n"
            
            # 提取文本
            blocks = page.get_text("text")
            text += blocks
        
        doc.close()
        return text
    except Exception as e:
        print(f"pymupdf 提取错误: {e}")
        return ""

def parse_bank_transactions_from_text(text):
    """从文本中解析银行流水交易记录"""
    transactions = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # 尝试匹配银行流水格式
        # 格式示例: 2024-01-01 | 交易摘要 | 借方 | 贷方 | 余额
        if line and '20' in line[:10]:  # 简单判断是否包含日期
            # 尝试提取日期
            parts = line.split()
            if parts and len(parts) >= 3:
                transactions.append({
                    'line': i,
                    'raw_text': line,
                    'parts': parts
                })
    
    return transactions

def analyze_table_structure(tables):
    """分析表格结构"""
    if not tables:
        return "未找到表格数据"
    
    analysis = f"\n{'='*80}\n"
    analysis += "表格结构分析\n"
    analysis += f"{'='*80}\n"
    analysis += f"总表格数: {len(tables)}\n\n"
    
    for i, table in enumerate(tables[:3]):  # 只分析前3个表格
        if table and len(table) > 0:
            analysis += f"表格 {i+1}:\n"
            analysis += f"  行数: {len(table)}\n"
            if len(table) > 0:
                analysis += f"  列数: {len(table[0])}\n"
                analysis += "  表头: " + " | ".join([str(cell)[:20] for cell in table[0]]) + "\n"
                if len(table) > 1:
                    analysis += "  示例行: " + " | ".join([str(cell)[:15] if cell else "" for cell in table[1]]) + "\n"
            analysis += "\n"
    
    return analysis

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 extract_pdf_advanced.py <pdf路径> [输出路径]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        output_path = "pdf_extracted_text_advanced.txt"
    
    print(f"\n正在提取: {pdf_path}")
    print(f"输出文件: {output_path}")
    print("="*80)
    
    # 尝试用pdfplumber提取（更适合表格）
    text_pdfplumber, tables = extract_with_pdfplumber(pdf_path)
    
    # 尝试用pymupdf提取
    text_fitz = extract_with_fitz(pdf_path)
    
    # 比较两种方法的结果
    print("\n" + "="*80)
    print("提取结果对比:")
    print(f"  pdfplumber: {len(text_pdfplumber)} 字符, {len(tables)} 个表格")
    print(f"  pymupdf: {len(text_fitz)} 字符")
    
    # 选择最佳结果
    if len(tables) > 0:
        text = text_pdfplumber
        print("\n使用 pdfplumber 的结果（包含表格数据）")
    elif len(text_fitz) > len(text_pdfplumber):
        text = text_fitz
        print("\n使用 pymupdf 的结果（文本更完整）")
    else:
        text = text_pdfplumber
        print("\n使用 pdfplumber 的结果")
    
    # 分析表格结构
    table_analysis = analyze_table_structure(tables)
    
    # 保存结果
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
        f.write("\n\n")
        f.write(table_analysis)
    
    print(f"\n文本已保存到: {output_path}")
    print("="*80)
    
    # 打印预览
    preview_length = min(3000, len(text))
    print("\n" + "="*80)
    print("前3000字符预览:")
    print("="*80)
    print(text[:preview_length])
    print("\n" + table_analysis)
