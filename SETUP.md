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

> **Note:** On Mac, you will typically need to use `python3` and `pip3` instead of `python` and `pip`. The rest of this guide uses `python` and `pip` for brevity — substitute `python3`/`pip3` if you are on Mac.

### Windows

1. Download Python from [python.org/downloads](https://www.python.org/downloads/).
2. **Important:** During installation, check the box that says **"Add Python to PATH"** before clicking Install.
3. Verify by opening Git Bash and typing:
   ```bash
   python --version
   ```

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

> **Tip:** All commands from this point forward should be run from inside the `3250_class_project` folder. If you close and reopen your terminal, remember to `cd 3250_class_project` again.

---

## 4. Install Required Packages

Make sure you are inside the `3250_class_project` folder (see Step 3), then run:

```bash
pip install pandas numpy matplotlib
```

This installs:

| Package              | Purpose                        |
| -------------------- | ------------------------------ |
| **pandas**     | Data manipulation and analysis |
| **numpy**      | Numerical computing            |
| **matplotlib** | Plotting and visualization     |

---

## 5. Verify Everything Works

Open a Python prompt and try importing the project's dependencies:

```bash
python -c "import pandas; import numpy; import matplotlib; print('All packages installed successfully!')"
```

If you see `All packages installed successfully!`, you're all set. If you get an error like `ModuleNotFoundError`, re-run the `pip install` command from Step 4.

---

## 6. Basic Git Workflow

Since this is a group project, everyone pushes changes to the same repository. Here is the basic workflow:

### Before you start working

Always pull the latest changes first so you're not working on outdated code:

```bash
git pull
```

### Creating a branch

Work on a separate branch to avoid conflicts with others:

```bash
git checkout -b your-name/short-description
```

For example: `git checkout -b leo/add-inflation-script`

### Saving and pushing your work

```bash
git add <files you changed>       # Stage specific files
git commit -m "Brief description of what you did"
git push -u origin branch-name
```

Then open a **Pull Request** on GitHub to merge your branch into `main`.

- Make sure your commit messages are detailed enough for users that didn't work with you to know what you accomplished without having to read through your code. "quick fixes" is not an acceptable commit message.

### If you get a merge conflict

1. Run `git pull` to fetch the latest changes.
2. Git will mark the conflicting lines in the file. Open the file, pick the correct version, and remove the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
3. Stage and commit the resolved file.

> **Tip:** Commit and push often. Small, frequent commits are much easier to merge than one giant change at the end.

---

## Quick Reference

| Task                          | Command                                   |
| ----------------------------- | ----------------------------------------- |
| Pull the latest changes       | `git pull`                              |
| Create a new branch           | `git checkout -b your-name/description` |
| Check which files you changed | `git status`                            |
| Stage files for commit        | `git add <filename>`                    |
| Commit your changes           | `git commit -m "message"`               |
| Push your branch              | `git push -u origin branch-name`        |
| Run all tests                 | `pytest tests/`                         |

---

## Troubleshooting

- **`pip` not found:** Try `pip3` instead of `pip`, or `python -m pip install ...`.
- **Permission denied:** Add `--user` to the install command: `pip install --user pandas numpy matplotlib pytest`.
- **`python` not found on Windows:** Reinstall Python and make sure you checked **"Add Python to PATH"**.
- **`git` not recognized on Windows:** Make sure you're using **Git Bash**, not the regular Command Prompt.
- **Tests fail with `ModuleNotFoundError`:** You are missing a package — re-run the `pip install` command from Step 4.
- **Merge conflicts:** See the "If you get a merge conflict" section above.


!!! If you look through this checklist and follow the steps, but still are unable to download or run into some undocumented issues, reach out in the groupme.
