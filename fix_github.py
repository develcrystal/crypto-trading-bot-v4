#!/usr/bin/env python
"""
GitHub Default Branch Switcher
Setzt main als Default Branch und löscht alte Branches
"""

import os
import sys

# Windows Console Encoding Fix
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

def fix_github_repository():
    """Repariert das GitHub Repository"""
    
    print("[FIX] Fixing GitHub repository default branch...")
    
    # 1. Delete alte branches die verwirren
    old_branches = [
        "v4-production-ready",
        "feature/dashboard-enhancements"
    ]
    
    for branch in old_branches:
        os.system(f'git push origin --delete {branch}')
        print(f"[DELETE] Removed branch: {branch}")
    
    # 2. Force push clean main
    os.system('git push -f origin main')
    print("[PUSH] Force pushed clean main branch")
    
    # 3. Set main as default
    print("[INFO] Set main as default branch on GitHub:")
    print("Go to: Settings > General > Default branch > Switch to main")
    
    print("[SUCCESS] Repository should now show clean version!")

if __name__ == "__main__":
    fix_github_repository()
