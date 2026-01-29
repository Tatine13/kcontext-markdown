#!/usr/bin/env python3
import os
import json
import sys
from pathlib import Path
import subprocess
import mimetypes
import shlex

# --- Configuration ---
APP_NAME = "KContext Markdown"
VERSION = "1.0.0"
TEMP_DATA = Path("/tmp/tempmd_data.json")
SERVICEMENU_DIR = Path.home() / ".local/share/kio/servicemenus"
BIN_PATH = Path.home() / ".local/bin/kcontext.py"

def load_data():
    if TEMP_DATA.exists():
        try:
            with open(TEMP_DATA, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_data(data):
    with open(TEMP_DATA, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    generate_servicemenu(data)

def is_text_file(filepath):
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.java', '.c', '.cpp', '.h', '.hpp',
        '.css', '.html', '.xml', '.json', '.yaml', '.yml', '.toml', '.ini',
        '.sh', '.bash', '.zsh', '.fish', '.conf', '.cfg', '.log',
        '.rs', '.go', '.php', '.rb', '.pl', '.lua', '.vim', '.tex',
        '.sql', '.r', '.m', '.swift', '.kt', '.ts', '.tsx', '.jsx',
        '.vue', '.svelte', '.gradle', '.cmake', '.makefile', '.dockerfile',
        '.gitignore', '.gitattributes', '.editorconfig'
    }

    path_obj = Path(filepath)
    name = path_obj.name.lower()

    if name == ".env.example" or name == "env.example":
        return True

    special_names = {'makefile', 'dockerfile', 'rakefile', 'gemfile'}
    if name in special_names or name.lstrip('.') in special_names:
        return True

    suffix = path_obj.suffix.lower()
    if suffix and suffix in text_extensions:
        return True

    try:
        mime, _ = mimetypes.guess_type(str(path_obj))
    except Exception:
        mime = None
    if mime and mime.startswith('text/'):
        return True

    try:
        if path_obj.is_file():
            size = path_obj.stat().st_size
            if 0 < size < 4 * 1024:
                try:
                    with open(path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                        sample = f.read(512)
                        nonprint = sum(1 for ch in sample if ord(ch) < 9 and ch not in ("\n", "\r", "\t"))
                        if nonprint == 0:
                            return True
                except Exception:
                    pass
    except Exception:
        pass

    return False

def read_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            return f"[Erreur de lecture: {str(e)}]"

def format_as_markdown(filepath, content):
    path_obj = Path(filepath)
    if path_obj.name.lower() in (".env.example", "env.example"):
        extension = 'env.example'
    else:
        extension = path_obj.suffix[1:] if path_obj.suffix else 'txt'

    md = f"### 📄 {path_obj.name}\n"
    md += f"**Path:** `{filepath}`\n\n"
    md += f"```{extension}\n"
    md += content
    md += "\n```\n\n"
    return md

def collect_files_recursive(path):
    files = []
    path_obj = Path(path)

    if path_obj.is_file():
        if is_text_file(path_obj):
            files.append(str(path_obj))
    elif path_obj.is_dir():
        for item in path_obj.rglob('*'):
            if item.is_file() and is_text_file(item):
                files.append(str(item))
    return files

def store_files(filepaths):
    data = load_data()
    existing_paths = {item['path'] for item in data}

    files_direct = []
    dirs = []
    for p in filepaths:
        pth = Path(p)
        if pth.is_file():
            files_direct.append(str(pth))
        elif pth.is_dir():
            dirs.append(str(pth))
        else:
            s = str(p)
            if s.startswith('file://'):
                s = s[7:]
            pth = Path(s)
            if pth.is_file():
                files_direct.append(str(pth))
            elif pth.is_dir():
                dirs.append(str(pth))

    all_to_add = []

    for f in files_direct:
        if f not in existing_paths and f not in all_to_add and is_text_file(f):
            all_to_add.append(f)

    for d in dirs:
        collected = collect_files_recursive(d)
        for f in collected:
            if f not in existing_paths and f not in all_to_add:
                all_to_add.append(f)

    for f in all_to_add:
        content = read_file_content(f)
        data.append({
            'path': f,
            'content': content,
            'name': Path(f).name
        })

    save_data(data)

def generate_markdown():
    data = load_data()
    if not data:
        return "# 📚 Temporary Files Collection\n\n*No files stored yet*\n"

    md = "# 📚 Temporary Files Collection\n\n"
    md += f"*Generated from {len(data)} file(s)*\n\n"
    md += "---\n\n"

    for item in data:
        md_block = format_as_markdown(item['path'], item['content'])
        md += md_block

    return md

def copy_to_clipboard():
    md_content = generate_markdown()
    try:
        process = subprocess.Popen(['xclip', '-selection', 'clipboard'],
                                   stdin=subprocess.PIPE)
        process.communicate(md_content.encode('utf-8'))
    except FileNotFoundError:
        try:
            process = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
            process.communicate(md_content.encode('utf-8'))
        except FileNotFoundError:
            subprocess.run(['kdialog', '--error',
                          'xclip or wl-copy not found.\nInstall: sudo apt install xclip'])

def drop_tempmd(target_dir):
    data = load_data()
    if not data:
        return

    md_content = generate_markdown()
    output_file = Path(target_dir) / "temp_collection.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    save_data([])

def drop_with_dialog():
    data = load_data()
    if not data:
        subprocess.run(['kdialog', '--sorry', 'No files stored!'])
        return

    result = subprocess.run(['kdialog', '--getexistingdirectory', str(Path.home())],
                           capture_output=True, text=True)

    if result.returncode == 0 and result.stdout.strip():
        target_dir = result.stdout.strip()
        drop_tempmd(target_dir)

def show_metrics():
    data = load_data()
    if not data:
        subprocess.run(['kdialog', '--msgbox', 'No files stored!'])
        return

    nb_files = len(data)
    total_lines = sum(item['content'].count('\n') + 1 for item in data)
    md_content = generate_markdown()
    md_size = len(md_content.encode('utf-8'))

    if md_size < 1024:
        size_str = f"{md_size} B"
    elif md_size < 1024 * 1024:
        size_str = f"{md_size / 1024:.1f} KB"
    else:
        size_str = f"{md_size / (1024 * 1024):.1f} MB"

    message = f"""
═══════════════════════════
📊 Collection Metrics
═══════════════════════════

📁 Files stored: {nb_files}
📝 Total lines: {total_lines:,}
💾 MD size: {size_str}

Files list:
"""
    for item in data:
        message += f"  • {item['name']}\n"

    subprocess.run(['kdialog', '--title', 'Metrics', '--msgbox', message])

def remove_item(filepath):
    data = load_data()
    data = [item for item in data if item['path'] != filepath]
    save_data(data)

def clear_all():
    save_data([])

def generate_servicemenu(data):
    home = str(Path.home())
    script_path = str(Path(sys.argv[0]).resolve())

    file_menu_header = f"""
[Desktop Entry]
Type=Service
X-KDE-ServiceTypes=KonqPopupMenu/Plugin
MimeType=text/plain;text/x-python;text/x-c++;application/x-shellscript;text/markdown;application/json;text/x-tex;text/x-csrc;text/x-chdr;text/html;text/css;application/javascript;text/x-java;application/x-yaml;
Actions="""

    folder_menu_header = f"""
[Desktop Entry]
Type=Service
X-KDE-ServiceTypes=KonqPopupMenu/Plugin
MimeType=inode/directory;
Actions="""

    common_actions = f"""

[Desktop Action StoreInTempMD]
Name=➕ Add to KContext
Icon=document-save
Exec={script_path} store %U

[Desktop Action CopyToClipboard]
Name=📋 Copy Collection to Clipboard
Icon=edit-copy
Exec={script_path} copy

[Desktop Action DropTempMD]
Name=📁 Drop Collection Here
Icon=document-export
Exec={script_path} drop %f
"""

    file_actions = ["StoreInTempMD", "CopyToClipboard"]
    folder_actions = ["StoreInTempMD", "CopyToClipboard", "DropTempMD"]
    manage_actions = ""

    if data:
        file_actions.append("SeparatorFiles")
        folder_actions.append("SeparatorFiles")
        manage_actions += "\n[Desktop Action SeparatorFiles]\nName=--- Stored Files ---\nExec=/bin/true\n\n"

        for i, item in enumerate(data):
            action_name = f"RemoveItem{i}"
            file_actions.append(action_name)
            folder_actions.append(action_name)
            quoted_path = shlex.quote(item['path'])
            manage_actions += f"""
[Desktop Action {action_name}]
Name=❌ {item['name']}
Icon=edit-delete
Exec={script_path} remove {quoted_path}

"""

    if data:
        nb_files = len(data)
        total_lines = sum(item['content'].count('\n') + 1 for item in data)
        metrics_name = f"📊 Metrics ({nb_files} files)"
    else:
        metrics_name = "📊 Metrics (Empty)"

    file_actions.extend(["ShowMetrics", "ClearAll"])
    folder_actions.extend(["ShowMetrics", "ClearAll"])

    manage_actions += f"""

[Desktop Action ShowMetrics]
Name={metrics_name}
Icon=view-statistics
Exec={script_path} metrics

[Desktop Action ClearAll]
Name=🗑️ Clear Collection
Icon=edit-clear-all
Exec={script_path} clear
"""

    file_menu = file_menu_header + ";".join(file_actions) + "\n" + common_actions + manage_actions
    folder_menu = folder_menu_header + ";".join(folder_actions) + "\n" + common_actions + manage_actions

    SERVICEMENU_DIR.mkdir(parents=True, exist_ok=True)
    with open(SERVICEMENU_DIR / "kcontext-files.desktop", 'w', encoding='utf-8') as f:
        f.write(file_menu)
    with open(SERVICEMENU_DIR / "kcontext-folders.desktop", 'w', encoding='utf-8') as f:
        f.write(folder_menu)

    try:
        subprocess.run(['kbuildsycoca5'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: kcontext.py [init|store|copy|drop|metrics|clear|remove] ...")
        sys.exit(1)

    action = sys.argv[1]

    if action == "store" and len(sys.argv) > 2:
        store_files(sys.argv[2:])
    elif action == "copy":
        copy_to_clipboard()
    elif action == "drop" and len(sys.argv) > 2:
        drop_tempmd(sys.argv[2])
    elif action == "drop-dialog":
        drop_with_dialog()
    elif action == "metrics":
        show_metrics()
    elif action == "remove" and len(sys.argv) > 2:
        path_to_remove = " ".join(sys.argv[2:])
        if path_to_remove.startswith("'"') and path_to_remove.endswith("'"'):
            path_to_remove = path_to_remove[1:-1]
        remove_item(path_to_remove)
    elif action == "clear":
        clear_all()
    elif action == "init":
        generate_servicemenu(load_data())
        print(f"\n✅ KContext Markdown installed! KDE Menu updated.")
    else:
        print("Unknown command")