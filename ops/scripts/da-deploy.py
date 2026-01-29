#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

"""
DA-OMNI-SCOUT: MULTI-DEVICE DEPLOYMENT ENGINE
Version: 1.7.0
Feature: Fractal Indexing (Index in EVERY folder) + Intelligent Master Aggregator.
"""

def setup_directories():
    print("📂 Initializing Da-Scout Directory Mesh...")
    dirs = ["~/ops/gems", "~/ops/archive/raw", "~/ops/knowledge_base", "~/ops/gdrive", "~/.config/fish/functions"]
    for d in dirs:
        os.makedirs(os.path.expanduser(d), exist_ok=True)

def deploy_fish_functions():
    print("🐟 Injecting v1.7.0 Fractal Indexer...")
    functions = {
        "da-index": """function da-index --description "Fractal Indexing Engine (Local + Recursive)"
    set target_dir $argv[1]; if test -z "$target_dir"; set target_dir .; end
    set abs_target (realpath $target_dir)
    
    echo "🌀 Commencing Fractal Scan: $abs_target"
    
    # 1. Identify all non-hidden directories
    find "$abs_target" -type d -not -path '*/.*' | while read -l dir
        set index_file "$dir/DIRECTORY_INDEX.md"
        
        # 2. Extract contents (excluding hidden and indexes)
        set files (ls -p $dir | grep -v / | grep -v "INDEX.md")
        set subdirs (ls -p $dir | grep / | grep -v ".*" | string replace '/' '')

        if test -n "$files" -o -n "$subdirs"
            if test -f "$index_file"; rm "$index_file"; end
            
            echo "# 📂 INDEX: $(string replace (realpath $HOME) '~' (realpath $dir))" > "$index_file"
            echo "**Scan Date:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$index_file"
            echo "---" >> "$index_file"
            
            if test -n "$subdirs"
                echo "## 📁 SUBDIRECTORIES" >> "$index_file"
                for s in $subdirs
                    echo "- [ ] 📂 [$s/](./$s/)" >> "$index_file"
                end
                echo "" >> "$index_file"
            end

            if test -n "$files"
                echo "## 📄 FILES" >> "$index_file"
                for file in $files
                    set size (du -h "$dir/$file" | cut -f1)
                    set mod (date -r "$dir/$file" '+%Y-%m-%d')
                    echo "- [ ] **$file** | $size | $mod" >> "$index_file"
                end
            end
        end
    end
    echo "✅ Fractal Indexing complete."
end""",
        "da-master-index": """function da-master-index --description "Global Master Index Aggregator"
    set master_file "$HOME/MASTER_INDEX.md"
    echo "🏗️  Synthesizing Master Index..."
    
    if test -f "$master_file"; rm "$master_file"; end
    
    echo "# DA-OMNI-SCOUT: GLOBAL MASTER INDEX" > "$master_file"
    echo "**Node:** $(hostname) | **Arch:** $(uname -m)" >> "$master_file"
    echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$master_file"
    echo "---" >> "$master_file"
    
    # Summary of Key Hubs
    echo "## 📍 QUICK LINKS" >> "$master_file"
    echo "- [Documents Folder](~/Documents)" >> "$master_file"
    if test -d "$HOME/ops"; echo "- [Ops Infrastructure](~/ops)" >> "$master_file"; end
    if test -d "$HOME/Desktop"; echo "- [Desktop Workspace](~/Desktop)" >> "$master_file"; end
    echo "---" >> "$master_file"

    # Aggregate all local indexes into one view
    find $HOME -maxdepth 4 -name "DIRECTORY_INDEX.md" -not -path '*/.*' | sort | while read -l idx
        set dir_path (dirname $idx)
        set relative_dir (string replace $HOME '~' $dir_path)
        echo "" >> "$master_file"
        echo "### 📂 $relative_dir" >> "$master_file"
        # Pull only the file list from the local index to keep master clean
        grep "^\- \[ \] \*\*" "$idx" >> "$master_file"
    end
    
    echo "✅ MASTER INDEX synthesized from fractal data."
end""",
        "da-stats": """function da-stats --description "Mesh Resource Intel"
    echo "📊 SYSTEM INTEL: $(hostname)"
    echo "---"
    echo "💾 Disk Usage: $(df -h / | tail -1 | awk '{print $5}')"
    echo "🧠 Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
    echo "🌡️  CPU Load: $(uptime | awk -F'load average:' '{ print $2 }')"
    echo "🌐 Mesh IP: $(tailscale ip -4 2>/dev/null || echo 'Offline')"
end"""
    }

    for name, body in functions.items():
        path = os.path.expanduser(f"~/.config/fish/functions/{name}.fish")
        with open(path, "w") as f:
            f.write(body)
        print(f"  [+] Synced: {name}.fish")

if __name__ == "__main__":
    setup_directories()
    deploy_fish_functions()
    print("\n✅ DA-OMNI-SCOUT v1.7.0 FRACTAL DEPLOYMENT COMPLETE.")
