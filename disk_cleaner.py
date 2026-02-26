#!/usr/bin/env python3
"""
disk_cleaner.py - Finds unused files (45+ days) and asks whether to delete them
Works on Linux and Windows
"""

import os
import sys
import time
import platform
from pathlib import Path
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION
# ============================================================
DAYS_UNUSED = 45  # one and a half month

# Folders that will NEVER be scanned (system, boot, etc.)
SKIP_DIRS = {
    # Linux
    "/proc", "/sys", "/dev", "/run", "/boot", "/etc",
    "/usr/lib", "/usr/bin", "/usr/sbin", "/bin", "/sbin",
    "/lib", "/lib64", "/snap", "/var/lib", "/var/run",
    # Windows
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
    "C:\\ProgramData", "C:\\$Recycle.Bin", "C:\\System Volume Information",
    # Hidden system folders
    ".git", ".npm", ".cache", "node_modules", "__pycache__",
    ".local/share/flatpak", ".local/lib",
}

# Extensions to skip (system libraries, etc.)
SKIP_EXTENSIONS = {
    ".so", ".dll", ".sys", ".ko", ".mod",  # libraries/modules
    ".pyc", ".pyo",  # python cache
}

# ============================================================

def format_size(size_bytes):
    """Formats file size in a readable way"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def should_skip(path_str):
    """Checks if a folder/file should be skipped"""
    path_str_lower = path_str.lower()
    for skip in SKIP_DIRS:
        if path_str_lower.startswith(skip.lower()):
            return True
    return False

def get_last_used(filepath):
    """Returns the date the file was last used"""
    try:
        stat = os.stat(filepath)
        # Bierzemy najnowszą z: modyfikacja i dostęp
        last_used = max(stat.st_mtime, stat.st_atime)
        return datetime.fromtimestamp(last_used)
    except (PermissionError, OSError):
        return None

def scan_disk(root_path, cutoff_date):
    """Scans the disk and returns a list of unused files"""
    unused_files = []
    scanned = 0
    skipped = 0
    errors = 0

    print(f"\n🔍 Scanning: {root_path}")
    print(f"📅 Looking for files unused since: {cutoff_date.strftime('%d.%m.%Y')}")
    print("   (this may take a while...)\n")

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
        # Usuń z listy foldery do pominięcia (modyfikacja in-place)
        dirnames[:] = [
            d for d in dirnames
            if not should_skip(os.path.join(dirpath, d))
            and not d.startswith(".")  # ukryte foldery
        ]

        if should_skip(dirpath):
            skipped += 1
            continue

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            ext = Path(filename).suffix.lower()

            # Pomijamy systemowe rozszerzenia
            if ext in SKIP_EXTENSIONS:
                continue

            # Pomijamy dowiązania symboliczne
            if os.path.islink(filepath):
                continue

            try:
                last_used = get_last_used(filepath)
                if last_used is None:
                    errors += 1
                    continue

                scanned += 1
                if scanned % 500 == 0:
                    print(f"   Scanned: {scanned} files...", end="\r")

                if last_used < cutoff_date:
                    size = os.path.getsize(filepath)
                    unused_files.append({
                        "path": filepath,
                        "last_used": last_used,
                        "size": size
                    })

            except (PermissionError, OSError):
                errors += 1

    print(f"\n✅ Done! Scanned {scanned} files, errors skipped: {errors}")
    return unused_files

def display_results(unused_files):
    """Displays the list of unused files"""
    if not unused_files:
        print("\n🎉 No unused files found! Your disk is clean.")
        return

    # Sort by oldest first
    unused_files.sort(key=lambda x: x["last_used"])

    total_size = sum(f["size"] for f in unused_files)

    print(f"\n{'='*70}")
    print(f"📋 UNUSED FILES FOUND ({len(unused_files)} total)")
    print(f"{'='*70}")
    print(f"{'#':<5} {'Last used':<20} {'Size':<12} Path")
    print(f"{'-'*70}")

    for i, f in enumerate(unused_files, 1):
        date_str = f["last_used"].strftime("%d.%m.%Y")
        size_str = format_size(f["size"])
        path = f["path"]
        # Shorten long paths
        if len(path) > 50:
            path = "..." + path[-47:]
        print(f"{i:<5} {date_str:<20} {size_str:<12} {path}")

    print(f"{'-'*70}")
    print(f"💾 Total size to reclaim: {format_size(total_size)}")
    print(f"{'='*70}")

def ask_and_delete(unused_files):
    """Asks the user and deletes files"""
    print("\n❓ Do you want to delete these files?")
    print("   [y] - yes, delete all")
    print("   [n] - no, exit")
    print("   [s] - select which ones to delete")

    choice = input("\nYour choice: ").strip().lower()

    if choice == "n":
        print("\n👋 Cancelled. No files were deleted.")
        return

    elif choice == "y":
        files_to_delete = unused_files

    elif choice == "s":
        print("\nEnter file numbers to delete (e.g: 1 3 5 or 1-10):")
        selection = input("Numbers: ").strip()
        files_to_delete = []

        try:
            for part in selection.split():
                if "-" in part:
                    start, end = part.split("-")
                    for i in range(int(start), int(end) + 1):
                        if 1 <= i <= len(unused_files):
                            files_to_delete.append(unused_files[i - 1])
                else:
                    i = int(part)
                    if 1 <= i <= len(unused_files):
                        files_to_delete.append(unused_files[i - 1])
        except ValueError:
            print("❌ Invalid format. Cancelled.")
            return
    else:
        print("❌ Unknown option. Cancelled.")
        return

    # Confirm before deleting
    total = format_size(sum(f["size"] for f in files_to_delete))
    print(f"\n⚠️  About to delete {len(files_to_delete)} files ({total})")
    confirm = input("Are you sure? (type 'yes' to confirm): ").strip().lower()

    if confirm != "yes":
        print("👋 Cancelled.")
        return

    # Deleting
    deleted = 0
    failed = 0
    print("\n🗑️  Deleting...")

    for f in files_to_delete:
        try:
            os.remove(f["path"])
            deleted += 1
        except (PermissionError, OSError) as e:
            print(f"   ❌ Cannot delete: {f['path']} ({e})")
            failed += 1

    print(f"\n✅ Deleted: {deleted} files")
    if failed:
        print(f"❌ Failed: {failed} files (no permission or locked)")

def main():
    print("=" * 70)
    print("🧹 DISK CLEANER - Find and remove unused files")
    print("=" * 70)

    # Detect system and set default root
    system = platform.system()
    if system == "Windows":
        default_root = "C:\\"
    else:
        default_root = str(Path.home())  # Default to home directory on Linux

    print(f"\n💻 System: {system}")
    print(f"📁 Default path: {default_root}")
    print("\nWhere to scan?")
    print(f"  [Enter] - {default_root} (default)")
    print("  [other] - type your own path")

    user_path = input("\nPath: ").strip()
    root_path = user_path if user_path else default_root

    if not os.path.exists(root_path):
        print(f"❌ Path does not exist: {root_path}")
        sys.exit(1)

    cutoff_date = datetime.now() - timedelta(days=DAYS_UNUSED)

    # Scan
    unused_files = scan_disk(root_path, cutoff_date)

    # Show results
    display_results(unused_files)

    if unused_files:
        ask_and_delete(unused_files)

    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
