import os
import sys
import subprocess

def align_all(skills_root):
    """
    遍历所有技能目录，对每个包含 evolution.json 的技能运行 smart_stitch.py
    """
    # 检查技能根目录是否存在
    if not os.path.exists(skills_root):
        print(f"Error: Skills root directory '{skills_root}' does not exist")
        return
    
    # 获取 smart_stitch.py 的路径（与当前脚本在同一目录）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    smart_stitch_path = os.path.join(current_dir, "smart_stitch.py")
    
    if not os.path.exists(smart_stitch_path):
        print(f"Error: smart_stitch.py not found at {smart_stitch_path}")
        return
    
    aligned_count = 0
    
    # 遍历所有技能目录
    for skill_name in os.listdir(skills_root):
        skill_dir = os.path.join(skills_root, skill_name)
        
        # 只处理目录
        if not os.path.isdir(skill_dir):
            continue
        
        # 检查是否存在 evolution.json
        evolution_path = os.path.join(skill_dir, "evolution.json")
        if os.path.exists(evolution_path):
            print(f"Aligning: {skill_name}")
            try:
                # 调用 smart_stitch.py
                subprocess.run(
                    [sys.executable, smart_stitch_path, skill_dir],
                    check=True,
                    capture_output=True,
                    text=True
                )
                aligned_count += 1
            except subprocess.CalledProcessError as e:
                print(f"Error aligning {skill_name}: {e}")
                print(f"stdout: {e.stdout}")
                print(f"stderr: {e.stderr}")
    
    print(f"\nAlignment complete. Total aligned skills: {aligned_count}")

if __name__ == "__main__":
    # 默认技能目录
    default_skills_root = r"/Users/jj/CodeBuddy/skill"
    
    # 使用命令行参数或默认路径
    skills_root = sys.argv[1] if len(sys.argv) > 1 else default_skills_root
    
    align_all(skills_root)
