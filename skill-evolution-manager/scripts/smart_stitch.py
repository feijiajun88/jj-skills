import os
import sys
import json
import re

def stitch_skill(skill_dir):
    """
    读取evolution.json并将其缝合到SKILL.md的专用部分
    """
    evolution_path = os.path.join(skill_dir, "evolution.json")
    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    
    # 检查文件是否存在
    if not os.path.exists(evolution_path):
        print(f"No evolution.json found in {skill_dir}")
        return False
    
    if not os.path.exists(skill_md_path):
        print(f"No SKILL.md found in {skill_dir}")
        return False
    
    # 读取 evolution.json
    with open(evolution_path, 'r', encoding='utf-8') as f:
        evolution_data = json.load(f)
    
    # 生成 Markdown 内容块
    markdown_content = generate_evolution_section(evolution_data)
    
    # 读取 SKILL.md
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        skill_content = f.read()
    
    # 检查是否已存在该章节
    section_pattern = r'## User-Learned Best Practices & Constraints\s*\n(.*?)(?=\n##|\Z)'
    existing_match = re.search(section_pattern, skill_content, re.DOTALL)
    
    if existing_match:
        # 更新现有章节
        updated_content = re.sub(section_pattern, markdown_content, skill_content, count=1, flags=re.DOTALL)
    else:
        # 追加新章节
        updated_content = skill_content + "\n\n" + markdown_content
    
    # 写回 SKILL.md
    with open(skill_md_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Successfully stitched evolution data into {skill_dir}")
    return True

def generate_evolution_section(evolution_data):
    """
    根据 evolution_data 生成格式化的 Markdown 章节
    """
    lines = ["## User-Learned Best Practices & Constraints\n"]
    
    # User Preferences
    if 'preferences' in evolution_data and evolution_data['preferences']:
        lines.append("### User Preferences\n")
        for pref in evolution_data['preferences']:
            lines.append(f"- {pref}\n")
        lines.append("\n")
    
    # Known Fixes & Workarounds
    if 'fixes' in evolution_data and evolution_data['fixes']:
        lines.append("### Known Fixes & Workarounds\n")
        for fix in evolution_data['fixes']:
            lines.append(f"- {fix}\n")
        lines.append("\n")
    
    # Custom Instruction Injection
    if 'custom_prompts' in evolution_data and evolution_data['custom_prompts']:
        lines.append("### Custom Instruction Injection\n")
        lines.append(f"{evolution_data['custom_prompts']}\n\n")
    
    # Last Updated
    if 'last_updated' in evolution_data:
        lines.append(f"*Last updated: {evolution_data['last_updated']}*\n")
    
    return "".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_stitch.py <skill_directory>")
        sys.exit(1)
    
    skill_dir = sys.argv[1]
    stitch_skill(skill_dir)
