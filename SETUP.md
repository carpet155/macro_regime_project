# Getting Started

A step-by-step guide for setting up this project on your computer. No prior experience with Git or the command line is required.

---

## 1. Install Git

Git is a version control tool that lets you download and collaborate on code.

### Mac

1. Open **Terminal** (search "Terminal" in Spotlight with `Cmd + Space`).
2. Type the following and press Enter:
   ```bash
   git --version
   ```
3. If Git is not installed, macOS will prompt you to install the **Xcode Command Line Tools**. Click **Install** and follow the prompts.
4. Once finished, run `git --version` again to confirm it works.

### Windows

1. Download the Git installer from [git-scm.com/download/win](https://git-scm.com/download/win).
2. Run the installer. **Use the default options** at every step — just keep clicking Next.
3. Once installed, open **Git Bash** (search for it in the Start menu). This is the terminal you will use for all commands below.
4. Verify by typing:
   ```bash
   git --version
   ```

---

## 2. Install Python

This project requires **Python 3.8 or newer**.

### Mac

Python 3 may already be installed. Check by running:
```bash
python3 --version
```
If not installed, download it from [python.org/downloads](https://www.python.org/downloads/) and run the installer.

### Windows

1. Download Python from [python.org/downloads](https://www.python.org/downloads/).
2. **Important:** During installation, check the box that says **"Add Python to PATH"** before clicking Install.
3. Verify by opening Git Bash and typing:
   ```bash
   python --version
   ```

> **Note:** On Mac, you may need to use `python3` and `pip3` instead of `python` and `pip`.

---

## 3. Download the Project

Open your terminal (Terminal on Mac, Git Bash on Windows) and run:

```bash
git clone https://github.com/carpet155/3250_class_project.git
```

This creates a folder called `3250_class_project` with all the project files. Move into it:

```bash
cd 3250_class_project
```

---

## 4. Install Required Packages

Run this command inside the project folder:

```bash
pip install pandas numpy matplotlib pytest
```

This installs:
| Package | Purpose |
|---|---|
| **pandas** | Data manipulation and analysis |
| **numpy** | Numerical computing |
| **matplotlib** | Plotting and visualization |
| **pytest** | Running the test suite |

---

## 5. Verify Everything Works

Run the test suite to make sure the setup is correct:

```bash
pytest tests/
```

If the tests pass (or show expected skips), you're all set.

---

## Quick Reference

| Task | Command |
|---|---|
| Pull the latest changes | `git pull` |
| Check which files you changed | `git status` |
| Run all tests | `pytest tests/` |
| Run a specific script | `python scripts/ingest_inflation.py` |

---

## Troubleshooting

- **`pip` not found:** Try `pip3` instead of `pip`, or `python -m pip install ...`.
- **Permission denied:** Add `--user` to the install command: `pip install --user pandas numpy matplotlib pytest`.
- **`python` not found on Windows:** Reinstall Python and make sure you checked **"Add Python to PATH"**.
- **`git` not recognized on Windows:** Make sure you're using **Git Bash**, not the regular Command Prompt.
