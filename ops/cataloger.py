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
