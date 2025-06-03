# 🛠️ csProj Version Updater

A Python tool to update `<Version>` and `<AssemblyVersion>` elements in `.csproj` files recursively.

---

## 📌 Features

- ✅ Update existing `<Version>` and `<AssemblyVersion>` tags
- 🔍 Recursive scan of all `.csproj` files
- 🧠 Auto-detect version from the first `.csproj` if none is provided to setup Gui
- 💻 CLI or 🖱️ GUI (and ugly) modes
- 🧼 Does **not** insert `<?xml ... ?>` tags into `.csproj` files
- 🔒 Safe: skips `.csproj` files that don't already have these tags
- 🪟 GUI includes live console output

---

## 📦 Requirements

- Only built-in Python libraries are used:
- You may need to install tkinter if it is not included in your Python installation

pip install tkinter

## 🔹 GUI Mode (Default)
python csproj_updater.py
- Choose directory (optional)
- Enter version (pre-filled if available)
- Run update
- View console output directly in the window

## 🔹 CLI Silent Mode
python csproj_updater.py --silent Y --version 1.2.3.4

## ⚙️ Parameters

| Parameter          | Required              | Default | Description                                         |
| ------------------ | --------------------- | ------- | --------------------------------------------------- |
| `--silent`         | No                    | `N`     | If `Y`, runs in CLI mode                            |
| `--version`        | Yes (if `--silent Y`) |         | Version format `X.X.X.X`                            |
| `--root_dir_param` | No                    | `N`     | `Y` opens a dialog, `N` uses current dir            |
| `--root_dir`       | No                    |         | Predefines the root directory, skips prompt in CLI  |





## 📝 License
MIT License — Free to use, modify, and distribute.
