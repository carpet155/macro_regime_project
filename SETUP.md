
---

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

## 3. Workflow

Moving forward, each feature/change we work on will be its own branch and I’ll explain what that means. 

---

Here is your **complete, clean merged section** (Sections 4–8 + helpful commands), fully consistent with your existing `SETUP.md` style, with everything integrated:

---

## 4. Finding an Issue

To find an Issue to work on go to
[https://github.com/carpet155/macro_regime_project](https://github.com/carpet155/macro_regime_project)
and click on **Issues** at the top.

You will see a list of available issues. Click on one that you think you can tackle.

---

### Issues, Ownership, and Timeline

Issues in GitHub are mirrored in the Excel tracker.

Excel Tracker (timeline + contributions):
[https://myuva-my.sharepoint.com/:x:/g/personal/gng4fn_virginia_edu/IQCK-6tfyyD1RKthMXVus1bXAbZtbg9eqWFbcwxjVWgzi4w?e=oDW2Ho](https://myuva-my.sharepoint.com/:x:/g/personal/gng4fn_virginia_edu/IQCK-6tfyyD1RKthMXVus1bXAbZtbg9eqWFbcwxjVWgzi4w?e=oDW2Ho)

GitHub Milestones (organized by section + week):
[https://github.com/carpet155/macro_regime_project/milestones](https://github.com/carpet155/macro_regime_project/milestones)

Key rules:

* GitHub Assignee = source of truth for ownership
* Excel = contribution tracking + timeline through April 29
* You must update **both**
* Do NOT assign yourself in only one place

---

### Order of Work (Important)

* Work in **section order** (Setup → Pipeline → Cleaning → Feature Engineering → etc.)
* Follow **dates in Excel + milestones**

Some issues depend on previous ones:

* Example: You must clean data before creating features

Some issues are independent within a section

If unsure:

* Check milestone
* Check issue description
* Ask before skipping ahead

---

### How to Claim an Issue

When you open an issue page, look at the **right-hand panel**.

You will see:

**Assignees**

* If it says: *“No one – Assign yourself”*, it is available
* Click **Assign yourself** to claim it

**Development**

* This shows the **feature branch you must use**

Example:

```
feature/handle-nulls
```

---

### Process for Taking an Issue

1. Check Excel or GitHub milestones (timeline)
2. Make sure nobody owns it:

   * Check **Assignees (right panel)**
   * Check Excel tracker
3. Assign yourself on GitHub
4. Add yourself to Excel
5. Start work

---

## 5. Setup Steps

Once you get the branch name from the **Development section**, follow the steps below.

Steps:

1. Open Terminal on VSCode (or any coding platform)
2. Navigate to your STAT3250 Folder

Use:

```bash
cd path/to/your/folder
```

Then:

3.

```bash
git clone https://github.com/carpet155/macro_regime_project.git
```

4.

```bash
cd macro_regime_project
```

5.

```bash
git fetch origin
```

6.

```bash
git checkout (name of branch you want to work on)
```

EX:

```bash
git checkout feature/notebook-walkthrough
```

After Step 6, you are now working in your branch.

---

## 6. Doing Your Work

* Do your work that fulfills the GitHub Issue related to that branch. Try to not edit other files which are already in the branch. You should aim to only be adding files, if you remove/edit other files you may run into issues later on. If you must remove/edit other files and run into issues, you can ask me, Charlie, Leo, or ChatGPT/Claude for help.

---

## 7. Saving Your Work

Once you finish your work, go back in Terminal. You should follow the next 3 steps:

8.

```bash
git add .
```

The "." in Step 8 adds all the files you changed.

9.

```bash
git commit -m "(Literally can be anything inside the quotes)"
```

EX:

```bash
git commit -m "added missing macro handling logic"
```

10.

```bash
git push -u origin (name of branch you are working on)
```

EX:

```bash
git push -u origin feature/notebook-walkthrough
```

Now your changes are on GitHub. If you go to that branch on the GitHub repository, the files that you have on your computer should be the same files that show up on GitHub.

---

## 8. Creating a Pull Request

11. Now you can navigate to the GitHub main page:
    [https://github.com/carpet155/macro_regime_project](https://github.com/carpet155/macro_regime_project)

12. At the top of the page, click on **Pull Requests**

13. Click the green **“New Pull Request”** button

14. Keep:

* base → `main`
* compare → your branch

Then create the Pull Request.

Your pull request will remain open until other people review it and accept that pull request, which takes your work from your branch and adds it into the **main** branch.

Everyone will work like this and at the end the **main** branch will be our finished project.

---

## Helpful Commands

| Command                   | What it does                             |
| ------------------------- | ---------------------------------------- |
| `ls`                      | Shows files/folders in current directory |
| `cd folder_name`          | Moves into a folder                      |
| `cd ..`                   | Moves up one folder                      |
| `git clone <repo>`        | Downloads the repository                 |
| `cd macro_regime_project` | Moves into the project folder            |
| `git fetch origin`        | Gets latest branches from GitHub         |
| `git checkout <branch>`   | Switches to a branch                     |
| `git status`              | Shows current changes and branch         |
| `git add .`               | Stages all changes                       |
| `git commit -m "message"` | Saves your changes locally               |
| `git push`                | Uploads your changes to GitHub           |
| `git pull`                | Gets latest updates from remote          |
| `python --version`        | Checks Python version                    |
| `pip list`                | Shows installed packages                 |

---


