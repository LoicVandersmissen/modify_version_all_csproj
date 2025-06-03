import os
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import xml.etree.ElementTree as ET
import argparse

# -----------------------------
# Utility functions
# -----------------------------
def validate_version_format(version):
    parts = version.split('.')
    return len(parts) == 4 and all(part.isdigit() for part in parts)

def find_csproj_files(root_dir):
    csproj_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".csproj"):
                csproj_files.append(os.path.join(dirpath, file))
    return csproj_files

def extract_version_from_first_csproj(root_dir):
    for file_path in find_csproj_files(root_dir):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            for prop_group in root.findall(".//PropertyGroup"):
                for tag in ["Version", "AssemblyVersion"]:
                    elem = prop_group.find(tag)
                    if elem is not None and validate_version_format(elem.text):
                        return elem.text
        except Exception:
            continue
    return None

def update_csproj_versions(file_path, version):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        modified = False

        for prop_group in root.findall(".//PropertyGroup"):
            changed = False
            for tag in ["Version", "AssemblyVersion"]:
                elem = prop_group.find(tag)
                if elem is not None:
                    elem.text = version
                    changed = True
            if changed:
                modified = True

        if modified:
            tree.write(file_path, xml_declaration=False, encoding='utf-8')
            print(f"✅ Updated: {file_path}")
        else:
            print(f"⏭️ Skipped (no matching tags): {file_path}")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

# -----------------------------
# GUI-related classes
# -----------------------------
class ConsoleOutputRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self._stdout = sys.stdout
        self._stderr = sys.stderr

    def write(self, message):
        def write_to_widget():
            tag = 'error' if '❌' in message.lower() or 'error' in message.lower() else 'success' if '✅' in message else None
            self.text_widget.insert(tk.END, message, tag)
            self.text_widget.see(tk.END)

        self.text_widget.after(0, write_to_widget)
        self._stdout.write(message)

    def flush(self):
        self._stdout.flush()
        self._stderr.flush()

    def enable(self):
        sys.stdout = self
        sys.stderr = self

    def disable(self):
        sys.stdout = self._stdout
        sys.stderr = self._stderr

class CSProjUpdaterGUI:
    def __init__(self, root, default_version=None, default_root_dir_param='N', forced_root_dir=None):
        self.root = root
        self.root.title("CSProj Version Updater")
        self.root.geometry("700x450")
        self.root.resizable(False, False)

        self.use_gui_dir = tk.BooleanVar(value=(default_root_dir_param == 'Y'))
        self.selected_dir = tk.StringVar()
        self.version_parts = [tk.StringVar() for _ in range(4)]

        if forced_root_dir:
            self.selected_dir.set(forced_root_dir)
            self.use_gui_dir.set(True)

        if default_version and validate_version_format(default_version):
            parts = default_version.split('.')
            for i in range(4):
                self.version_parts[i].set(parts[i])
        else:
            inferred = extract_version_from_first_csproj(forced_root_dir or os.getcwd())
            if inferred and validate_version_format(inferred):
                for i, val in enumerate(inferred.split('.')):
                    self.version_parts[i].set(val)

        self.build_ui()

        self.redirector = ConsoleOutputRedirector(self.console_output)
        self.redirector.enable()

    def build_ui(self):
        frame = tk.Frame(self.root)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # Version label and fields
        tk.Label(frame, text="Version (format: X.X.X.X)").grid(row=0, column=0, sticky='w', pady=(0, 5))
        for i in range(4):
            entry = tk.Entry(frame, width=5, textvariable=self.version_parts[i])
            entry.grid(row=0, column=i + 1, padx=(2, 2), pady=(0, 5))

        # Checkbox for directory
        tk.Checkbutton(frame, text="Choose root directory", variable=self.use_gui_dir).grid(row=1, column=0, columnspan=5, sticky='w', pady=(0, 5))

        # Directory input and browse
        tk.Entry(frame, textvariable=self.selected_dir, width=50).grid(row=2, column=0, columnspan=4, sticky='w')
        tk.Button(frame, text="Browse", command=self.browse_dir).grid(row=2, column=4, padx=(5, 0), sticky='w')

        # Run button
        tk.Button(frame, text="Run Update", command=self.run_update).grid(row=3, column=2, sticky='e', pady=(5, 5))
        
        # Clear Output button
        tk.Button(frame, text="Clear Output", command=lambda: self.console_output.delete(1.0, tk.END)).grid(row=3, column=4, sticky='e', pady=(5, 5))

        # Output area
        self.console_output = ScrolledText(self.root, height=15, width=80, wrap=tk.WORD, state='normal')
        self.console_output.grid(row=4, column=0, padx=10, pady=10, columnspan=2)
        self.console_output.tag_config('error', foreground='red')
        self.console_output.tag_config('success', foreground='green')

    def browse_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.selected_dir.set(path)

    def run_update(self):
        version = '.'.join(var.get() for var in self.version_parts)
        if not validate_version_format(version):
            print("❌ Invalid version format. Use format X.X.X.X")
            return

        directory = self.selected_dir.get() if self.use_gui_dir.get() else os.getcwd()

        print(f"Running update in directory: {directory} with version: {version}")
        csproj_files = find_csproj_files(directory)
        for file in csproj_files:
            update_csproj_versions(file, version)

# -----------------------------
# Entry point
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', help="Version number in format X.X.X.X")
    parser.add_argument('--root_dir_param', choices=['Y', 'N'], default='N')
    parser.add_argument('--root_dir', help="Optional directory to use instead of current dir")
    parser.add_argument('--silent', choices=['Y', 'N'], default='N')
    args = parser.parse_args()

    if args.silent == 'Y':
        if not args.version or not validate_version_format(args.version):
            print("❌ In silent mode, you must provide a valid --version argument (X.X.X.X)")
            return
        directory = args.root_dir if args.root_dir else (os.getcwd() if args.root_dir_param == 'N' else filedialog.askdirectory())
        csproj_files = find_csproj_files(directory)
        for file in csproj_files:
            update_csproj_versions(file, args.version)
    else:
        root = tk.Tk()
        app = CSProjUpdaterGUI(root, default_version=args.version, default_root_dir_param=args.root_dir_param, forced_root_dir=args.root_dir)
        root.mainloop()

if __name__ == '__main__':
    main()
