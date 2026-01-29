THE DA-OMNI-SCOUT ARCHIVE & MESH MANUAL (COMPILATION)
Version: 4.0 (God-Tier Compilation) Status: ACTIVE Architect: Cody Evan Johnson Objective: A consolidated index of all code blocks, system configurations, and operational intelligence harvested from the "Da-Omni-Scout" reconnaissance loops.

I. THE FORGE: AUTOMATION & INTELLIGENCE TOOLS
Tools designed for harvesting, synthesizing, and organizing documentation.

1. The Engine: Gemini CLI
Role: The command-line interface for the AI model. Installation:

Bash

npm install -g @google/gemini-cli

+1

API Configuration: File: ~/.config/fish/config.fish

Bash

# Add this to ~/.config/fish/config.fish
set -gx GEMINI_API_KEY "YOUR_ACTUAL_API_KEY_HERE"


2. The Interface: dagem (The Flight Recorder)
Role: A specialized wrapper function that pipes user prompts and "Gem" personas into the CLI, while simultaneously logging the interaction to a "Black Box" JSON file. Evolution: evolved from a simple pipe (askgem) to a full logger.

File: ~/.config/fish/functions/dagem.fish (Final Version)

Bash

function dagem --description "Da-Gem v2: Pipe persona into Gemini AND log it"
    # Syntax: dagem [persona_name] "[prompt]"
    
    set gem_name $argv[1]
    set user_prompt $argv[2..-1] 
    set gem_path "$HOME/ops/gems/$gem_name.md"
    set timestamp (date "+%Y-%m-%d %H:%M:%S")
    set log_file "$HOME/ops/archive/raw/chat_history.jsonl"

    # Checks
    if not type -q gemini; echo "❌ Missing gemini-cli"; return 1; end
    if not set -q GEMINI_API_KEY; echo "❌ Missing API Key"; return 1; end

    if test -f "$gem_path"
        echo "💎 Spooling up Gem: $gem_name..."
        
        # 1. Run the AI and capture output to a variable AND print to screen
        # We use 'tee' to show it to you while capturing it
        set response (gemini chat --system "$(cat $gem_path)" -m "$user_prompt")
        echo $response | mdcat # Optional: use mdcat for pretty printing if installed

        # 2. The Black Box Recording (JSON Structure)
        # We escape quotes to prevent JSON breakage
        set safe_prompt (echo $user_prompt | string escape)
        set safe_response (echo $response | string escape)
        
        echo "{\"timestamp\": \"$timestamp\", \"gem\": \"$gem_name\", \"prompt\": \"$safe_prompt\", \"response\": \"$safe_response\"}" >> $log_file
        
        echo "💾 Interaction saved to Black Box."
    else
        echo "💀 Gem '$gem_name' not found."
    end
end

+2

3. The Sorter: librarian.py / cataloger.py
Role: The logic engine that parses the raw "Black Box" logs and organizes them into the directory schema. Evolution:

v1 (Librarian): Basic topic sorting.

v4 (Omniscient): Expanded into detailed silos.

Final (Cataloger): Includes "action item" triggers for documentation gaps.

File: cataloger.py (Final Standalone Version)

Python

import json
import os
import re
import hashlib

# CONFIGURATION
RAW_LOG = os.path.expanduser("~/ops/archive/raw/chat_history.jsonl")
KB_ROOT = os.path.expanduser("~/ops/knowledge_base")

# THE "CLEAN" SCHEMA
SCHEMA = {
    "meta": "00_INDEX",
    "nexus": "01_DA_NEXUS",
    "mobile": "02_DA_MOBILE_STACK",
    "pine": "03_DA_EDGE_STACK",
    "net": "04_NETWORK",
    "sec": "05_SECURITY",
    "code": "06_DEVELOPMENT",
    "sys": "07_SYSTEM_ADMIN",
    "ops": "08_ADMIN",
    "gear": "09_HARDWARE_INVENTORY",
    "core": "10_OS_INTERNALS",
    "ref": "11_REFERENCE",
    "void": "99_UNSORTED"
}

def sanitize(text):
    return re.sub(r'[^a-zA-Z0-9\-_]', '', text.replace(' ', '_')).lower()

def trigger_action_item(folder, sub_cat, filename, prompt):
    """Flags technical entries that require a formal reference entry."""
    action_path = os.path.join(KB_ROOT, SCHEMA["meta"], "documentation_triggers.md")
    os.makedirs(os.path.dirname(action_path), exist_ok=True)
    
    # Only trigger for technical/core categories that aren't already references
    technical_folders = [SCHEMA["code"], SCHEMA["sys"], SCHEMA["core"], SCHEMA["net"]]
    
    if folder in technical_folders:
        with open(action_path, 'a') as f:
            f.write(f"- [ ] **Ref Needed:** {folder}/{sub_cat} | *Source:* {filename} | *Topic:* {prompt[:50]}...\n")

def determine_routing(prompt, gem_name):
    p = prompt.lower()
    
    # --- 1. HARDWARE ---
    if any(x in p for x in ['hp', 'elitedesk', 'nexus', 'da-hp', 'backup', 'air-gap']):
        return SCHEMA["nexus"], "host_storage"
    if any(x in p for x in ['sata', 'ssd', 'hdd', 'raid']):
        return SCHEMA["nexus"], "storage_media"
    if any(x in p for x in ['pixel', 'android', 'phone', 'battery', 'daily', 'da-pixel']):
        return SCHEMA["mobile"], "android_daily"
    if any(x in p for x in ['termux', 'operator', 'git', 'push', 'rsync']):
        return SCHEMA["mobile"], "termux_env"
    if any(x in p for x in ['pinephone', 'pine', 'da-pine', 'sd card', 'boot']):
        return SCHEMA["pine"], "da_link"
    if any(x in p for x in ['emmc', 'rescue', 'repair', 'trauma', 'rebirth']):
        return SCHEMA["pine"], "da_rebirth_kit"

    # --- 2. PHYSICAL INVENTORY ---
    if any(x in p for x in ['mouse', 'keyboard', 'screen', 'monitor']):
        return SCHEMA["gear"], "peripherals"
    if any(x in p for x in ['power', 'psu', 'brick', 'cable', 'charger']):
        return SCHEMA["gear"], "power_components"
    if any(x in p for x in ['thumb drive', 'flash drive', 'enclosure']):
        return SCHEMA["gear"], "loose_media"
    if any(x in p for x in ['lshw', 'lsusb', 'serial', 'hardware id']):
        return SCHEMA["gear"], "specs_and_ids"

    # --- 3. OS INTERNALS ---
    if any(x in p for x in ['kernel', 'module', 'driver', 'modprobe']):
        return SCHEMA["core"], "kernel"
    if any(x in p for x in ['fstab', 'mount', 'inode', 'ext4', 'btrfs']):
        return SCHEMA["core"], "filesystem"
    if any(x in p for x in ['boot', 'grub', 'uefi', 'initramfs']):
        return SCHEMA["core"], "bootloader"
    if any(x in p for x in ['txt', 'conf', 'config', 'log file']):
        return SCHEMA["core"], "files_and_configs"

    # --- 4. NETWORK ---
    if any(x in p for x in ['tailscale', 'mesh', 'vpn', '100.']): return SCHEMA["net"], "vpn_mesh"
    if any(x in p for x in ['ip', 'port', 'dns', 'wifi', 'ethernet']): return SCHEMA["net"], "interfaces"

    # --- 5. DEVELOPMENT ---
    if any(x in p for x in ['python', 'fish', 'bash', 'script']): return SCHEMA["code"], "scripts"
    if any(x in p for x in ['gemini', 'ai', 'llm', 'token']): return SCHEMA["code"], "ai_tools"

    # --- 6. ADMIN ---
    if any(x in p for x in ['budget', 'cost', 'buy', 'order', 'deanna']):
        return SCHEMA["ops"], "finance"
    if any(x in p for x in ['plan', 'schedule', 'todo']):
        return SCHEMA["ops"], "projects"

    # --- 7. SYSTEM ADMIN ---
    if any(x in p for x in ['pacman', 'update', 'upgrade', 'install']): return SCHEMA["sys"], "packages"
    if any(x in p for x in ['systemd', 'service', 'journal']): return SCHEMA["sys"], "services"

    # --- 8. REFERENCE ---
    if any(x in p for x in ['manual', 'guide', 'man page']): return SCHEMA["ref"], "manuals"
    if any(x in p for x in ['index', 'map', 'list']): return SCHEMA["meta"], "indices"

    return SCHEMA["void"], "general"

def organize():
    if not os.path.exists(RAW_LOG):
        print("❌ CRITICAL: No flight recorder log found.")
        return

    print(f"📂 Da-Cataloger: Accessing Archives...")
    processed_count = 0
    
    with open(RAW_LOG, 'r') as f:
        for line in f:
            try:
                if not line.strip(): continue
                entry = json.loads(line)
            except json.JSONDecodeError: continue

            ts = entry.get('timestamp', 'Unknown')
            prompt = entry.get('prompt', '')
            response = entry.get('response', '')

            folder, sub_cat = determine_routing(prompt, "Da-Cataloger")
            save_dir = os.path.join(KB_ROOT, folder, sub_cat)
            os.makedirs(save_dir, exist_ok=True)

            prompt_slug = sanitize(prompt[:40])
            file_hash = hashlib.md5(prompt.encode()).hexdigest()[:6]
            filename = f"{ts[:10]}_{prompt_slug}_{file_hash}.md"
            file_path = os.path.join(save_dir, filename)

            if not os.path.exists(file_path):
                with open(file_path, 'w') as md:
                    md.write(f"# ARCHIVE: {folder}\n**Date:** {ts}\n**Unit:** {sub_cat}\n---\n\n## REQUEST\n{prompt}\n\n## OUTPUT\n{response}\n")
                
                # TRIGGER: Log as a documentation action item
                trigger_action_item(folder, sub_cat, filename, prompt)
                
                print(f"✅ Indexed: {folder}/{sub_cat}/{filename}")
                processed_count += 1

    print(f"🏁 Sort Complete. {processed_count} records filed by Da-Cataloger.")

if __name__ == "__main__":
    organize()
4. The Trigger: gemlib
Role: A shell alias to execute the Librarian/Cataloger script instantly. File: ~/.config/fish/functions/gemlib.fish

Bash

function gemlib --description "Run the Librarian to organize chat logs"
    echo "📚 Opening the stacks..."
    python3 ~/ops/librarian.py
end

+1

5. Utility Scripts
Gem Loader (loadgem.fish): Loads a persona into the clipboard.

Bash

function loadgem --description "Summon a Gem context to the clipboard"
    set gem_name $argv[1]
    set gem_path "$HOME/ops/gems/$gem_name.md"

    if test -f "$gem_path"
        if type -q wl-copy
            cat "$gem_path" | wl-copy
            echo "💎 Gem '$gem_name' loaded to clipboard. Just paste it."
        else if type -q xclip
            cat "$gem_path" | xclip -selection clipboard
            echo "💎 Gem '$gem_name' loaded to clipboard. Just paste it."
        else
            echo "❌ No clipboard tool found (install wl-clipboard or xclip)."
            echo "Here is the raw output:"
            cat "$gem_path"
        end
    else
        echo "💀 Gem not found. Available gems:"
        ls ~/ops/gems/ | sed 's/\.md//'
    end
end

6. The Interceptor: scout
Role: A wrapper function that intercepts standard commands, grabs raw help text (via --help or man), and forces the AI to generate a strict 8-5-4 Tiered Manual (Core, Dev, Scout flags). File: ~/.config/fish/functions/scout.fish

Bash

function scout --description "Generate 8-5-4 Manual for any command"
    set cmd_name $argv[1]
    
    # Check if the command exists
    if type -q $cmd_name
        echo "🔍 Scouting target: $cmd_name..."
        
        # Grab raw help (try --help first, fallback to man)
        set raw_intel ($cmd_name --help 2>&1)
        if test $status -ne 0
            set raw_intel (man $cmd_name | col -b)
        end
        
        # Fire the Omni-Scout Engine with the strict 8-5-4 directive
        dagem scout "Analyze this raw documentation for '$cmd_name' and generate a strict 8-5-4 Tiered Manual (8 Core, 5 Dev, 4 Scout Flags). RAW DATA: $raw_intel"
    else
        echo "❌ Target '$cmd_name' not found."
    end
end
7. The Neural Link: askops
Role: A search and retrieval tool using fzf and bat to instantly fuzzy-find and preview Markdown files within the Knowledge Base without leaving the terminal. File: ~/.config/fish/config.fish (Alias/Function)

Bash

# "Ask the Archives"
function askops
    cd ~/ops/knowledge_base
    # Find all .md files, fuzzy select one, and preview it with syntax highlighting
    set selected_file (find . -name "*.md" | fzf --preview "bat --style=numbers --color=always {}")
    
    if test -n "$selected_file"
        bat "$selected_file"
    end
    cd -
end
(Note: Requires pacman -S fzf bat)

8. The Autopsy: fixthis
Role: An error mitigation tool that captures the exit code and stderr of the last failed command ($history[1]) and pipes it to the coder Gem for immediate analysis and repair. File: ~/.config/fish/functions/fixthis.fish

Bash

function fixthis --description "Analyze the last failed command"
    # Note: In Fish, $history[1] is the last command.
    set last_cmd $history[1]
    
    echo "🚑 Analyzing failure: '$last_cmd'..."
    
    # Re-run the command to capture the error output specifically
    set error_log (eval $last_cmd 2>&1)
    
    dagem coder "The command '$last_cmd' failed. Here is the stderr output: \n\n $error_log \n\n Explain the error and provide the fixed command."
end

II. THE NEXUS: HOST CONFIGURATION
Hardware: HP EliteDesk 800 G1 (Haswell) | OS: CachyOS (Arch)

1. Kernel Tuning (UDP Optimization)
Objective: Optimize the Haswell CPU for high-bandwidth WireGuard/Tailscale traffic. File: /etc/sysctl.d/99-tailscale.conf

Ini, TOML

net.core.rmem_max = 2500000
net.core.wmem_max = 2500000
net.ipv4.tcp_keepalive_time = 600

+1

2. Service Optimization (CPU Priority)
Objective: Grant Syncthing high priority to prevent indexing lag. File: ~/.config/systemd/user/syncthing.service.d/override.conf

Ini, TOML

[Service]
Nice=-10
MemoryHigh=infinity

+1

3. Directory Structure
Objective: Establish the "Source of Truth" folder hierarchy. File: setup-anchor.sh

Bash

#!/bin/bash
mkdir -p ~/Sync/00-Inbox # Quick drops
mkdir -p ~/Sync/10-Code # GitHub Repos
mkdir -p ~/Sync/20-Notes # Obsidian
mkdir -p ~/Sync/30-Media # Images
chmod -R 750 ~/Sync


4. Defense in Depth (Versioning)
Layer A (Syncthing): Staggered versioning in config.xml.

XML

<versioning type="staggered">
<param key="cleanInterval" value="3600" />
<param key="maxAge" value="2592000" />
<param key="versionsPath" value=".stversions" />
</versioning>


Layer B (System): Btrfs snapshots via Snapper. Config: sudo snapper -c home_backup create-config /home Retention: Hourly=5, Daily=7. 

III. THE MOBILE STACK: CONFIGURATION
Hardware: Pixel 9 (Daily) & Termux (Operator)

1. Termux Auto-Start
Objective: Launch Syncthing automatically without root. File: ~/.bashrc

Bash

if ! pgrep -x "syncthing" > /dev/null; then
echo "Starting Syncthing..."
syncthing --no-browser --logfile=$HOME/syncthing.log &
fi


2. Termux Port Binding
Objective: Shift port to avoid conflicts with standard system ports. File: ~/.config/syncthing/config.xml

XML

<listenAddress>tcp://127.0.0.1:22001</listenAddress>
<globalAnnounceEnabled>false</globalAnnounceEnabled>


3. PRoot Container Linking
Objective: Share the "Code" folder from Termux to the Arch Linux container.

Bash

proot-distro login archlinux --bind $HOME/Sync/10-Code:/root/Code

+1

IV. THE EDGE STACK: PINEPHONE CONFIGURATION
Hardware: PinePhone (Allwinner Chip) | OS: Arch ARM

1. Resource Throttling
Objective: Prevent UI freezes during sync operations on low-RAM hardware. File: ~/.config/systemd/user/syncthing.service.d/lowmem.conf

Ini, TOML

[Service]
Nice=10
IOSchedulingClass=3
MemoryHigh=400M
MemoryMax=700M


2. Network Dependency
Objective: Ensure Tailscale is active before attempting sync. File: /etc/systemd/system/syncthing-wait.service

Ini, TOML

[Unit]
After=tailscaled.service
[Service]
ExecStart=/usr/bin/tailscale ping -c 1 100.100.100.100


V. GLOBAL REFERENCE & MESH LOGIC
1. The Master Ignore List
Objective: Prevent build artifacts from killing mobile battery life. File: .stignore

Plaintext

# Artifacts
node_modules
target
build
dist
venv
_pycache_
.git
.svn
# OS Junk
.DS_Store
Thumbs.db
*.swp


2. Synthetic Help Generation
Objective: POSIX-compliant help page for the custom mesh-manage tool.

Plaintext

NAME:
mesh-manage - Centralized controller for the Decentralized Mesh

USAGE:
mesh-manage [command] [options]

COMMANDS:
sync-start      Initialize Syncthing and Tailscale on this node.
sync-audit      Generate a report of out-of-sync files.
snap-create     Force an immediate Btrfs snapshot (Anchor only).
mesh-status     Check health of all 6 nodes defined in Hardware Register.

OPTIONS:
--force-wifi    Ignore Tailscale and attempt sync over local LAN.
--low-power     Activate PinePhone-specific resource throttling.
--help          Display this comprehensive manual.

EXIT CODES:
0               Success: Mesh is healthy.
1               Network Error: Tailscale interface down.
2               I/O Error: Disk full or Btrfs error.


VI. META: PERSONA DIRECTIVES
1. Da-Omni-Scout Engine
Directive: Act as a decentralized, recursive intelligence layer for harvesting system-native documentation. Output Standard (8-5-4):

Tier 8: Core Patterns (Health checks).

Tier 5: Dev-Level Flags (strace, memory dumps).

Tier 4: Scout Weapons (Obscure efficiency flags). 

2. Da-Architect Role Request
Trigger Prompt:

Plaintext

# Role Request: Activate "Da-Architect"
**Project Reference Log:**
* [Da-Scout]: Documentation_Engine_Config_2026
**Scout Report (Context Dump):**
The user wishes to build: A high-fidelity, cross-platform Documentation & Man-Page Generator.
**Contextual Intel:**
Hardware: HP EliteDesk, Pixel 9, Termux, PinePhone.
Stack: CachyOS, Arch Linux, Android 15.
