import sys
import os
import json
import yaml
import subprocess
import re

def parse_frontmatter(skill_md_path):
    """Parse YAML frontmatter from SKILL.md file."""
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parts = content.split('---')
        if len(parts) >= 3:
            return yaml.safe_load(parts[1])
    except Exception as e:
        print(f"Error parsing {skill_md_path}: {e}", file=sys.stderr)
    return None

def get_remote_hash(github_url):
    """Get the latest commit hash from GitHub using git ls-remote."""
    try:
        result = subprocess.run(
            ['git', 'ls-remote', github_url, 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return result.stdout.split()[0]
    except Exception as e:
        print(f"Error fetching remote hash for {github_url}: {e}", file=sys.stderr)
        return None

def scan_and_check(skills_root):
    """Scan all skills and check for updates."""
    if not os.path.exists(skills_root):
        print(f"Error: Skills directory not found: {skills_root}")
        return
    
    results = {
        'total': 0,
        'github_skills': 0,
        'outdated': [],
        'up_to_date': [],
        'errors': []
    }
    
    for skill_name in os.listdir(skills_root):
        skill_dir = os.path.join(skills_root, skill_name)
        if not os.path.isdir(skill_dir):
            continue
        
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_md):
            continue
        
        results['total'] += 1
        
        # Parse frontmatter
        meta = parse_frontmatter(skill_md)
        if not meta:
            continue
        
        # Check if it's a GitHub skill
        if 'github_url' not in meta:
            continue
        
        results['github_skills'] += 1
        
        local_hash = meta.get('github_hash', 'unknown')
        github_url = meta['github_url']
        
        # Fetch remote hash
        remote_hash = get_remote_hash(github_url)
        if not remote_hash:
            results['errors'].append({
                'name': skill_name,
                'url': github_url,
                'error': 'Failed to fetch remote hash'
            })
            continue
        
        # Compare hashes
        if local_hash == remote_hash:
            results['up_to_date'].append({
                'name': skill_name,
                'url': github_url,
                'hash': local_hash
            })
        else:
            results['outdated'].append({
                'name': skill_name,
                'url': github_url,
                'local_hash': local_hash,
                'remote_hash': remote_hash
            })
    
    # Print summary
    print("\n=== Skill Update Check Results ===")
    print(f"Total skills scanned: {results['total']}")
    print(f"GitHub-based skills: {results['github_skills']}")
    print(f"Up to date: {len(results['up_to_date'])}")
    print(f"Outdated: {len(results['outdated'])}")
    print(f"Errors: {len(results['errors'])}")
    
    if results['outdated']:
        print("\n--- Outdated Skills ---")
        for skill in results['outdated']:
            print(f"  - {skill['name']}")
            print(f"    URL: {skill['url']}")
            print(f"    Local:  {skill['local_hash'][:8]}...")
            print(f"    Remote: {skill['remote_hash'][:8]}...")
    
    if results['errors']:
        print("\n--- Errors ---")
        for error in results['errors']:
            print(f"  - {error['name']}: {error['error']}")
    
    # Export JSON
    return json.dumps(results, indent=2)

if __name__ == "__main__":
    skills_root = r"/Users/jj/CodeBuddy/skill"
    if len(sys.argv) > 1:
        skills_root = sys.argv[1]
    
    result_json = scan_and_check(skills_root)
    if result_json:
        print(f"\n--- JSON Output ---")
        print(result_json)
