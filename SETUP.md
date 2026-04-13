
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

Moving forward, each feature/change we work on will be its own branch and I’ll explain what that means. For now, I have deleted all the old branches before today, sorry.

---

## 4. Finding an Issue

To find an Issue to work on go to [https://github.com/carpet155/macro_regime_project](https://github.com/carpet155/macro_regime_project), and click on Issues at the top. Find any issue that you think you can tackle and click on it. Reference the shared excel link in GroupMe to add your name to that issue and confirm nobody else has assigned themselves that issue. Add your GitHub username to the Assignee section and add your name to the Excel (I will do this manually as well, GitHub assignee is the source of truth). In GitHub, you should see a screen like the one below. On the bottom right side there is “Development”, the branch you want to work on for this specific issue will be “feature/notebook-walkthrough”. This isn't the branch name for all the Issues, "feature/notebook-walkthrough" is just the name of the branch that I will refer to in the steps below as an example.

---

## 5. Setup Steps

Once you get that branch name, follow the steps below.

Steps:

1. Open Terminal on VSCode (or any coding platform)
2. Navigate to your STAT3250 Folder (or wherever you want to keep the files for this project)

This should be done using “cd”, if you don’t know what that means or how to navigate folders in Terminal, ask me, Charlie, Leo, or ChatGPT/Claude for help. "ls" might help too.

In Terminal type the following commands:

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

After Step 6, you are now working in your branch, you can exit Terminal.

---

## 6. Doing Your Work

7. Do your work that fulfills the GitHub Issue related to that branch. Try to not edit other files which are already in the branch. You should aim to only be adding files, if you remove/edit other files you may run into issues later on. If you must remove/edit other files and run into issues, you can ask me, Charlie, Leo, or ChatGPT/Claude for help.

---

## 7. Saving Your Work

Once you finish your work, go back in Terminal. you should follow the next 3 steps:

8.

```bash
git add .
```

The "." in Step 8 adds all the files you changed.

9.

```bash
git commit -m “(Literally can be anything inside the quotes)”
```

EX:

```bash
git commit -m “added X, updated Y, fixed Z”
```

10.

```bash
git push -u origin (name of branch you are working on)
```

EX:

```bash
git push -u origin feature/notebook-walkthrough
```

Now you have fully added all your changes into GItHub. If you go to that branch on the GitHub repository, the files that you have on your computer should be the same files that show up on GitHub.

---

## 8. Creating a Pull Request

11. Now you can navigate to the GitHub main page, [https://github.com/carpet155/macro_regime_project](https://github.com/carpet155/macro_regime_project)
12. At the top of the page, click on “Pull Requests”
13. Then click on the green “New Pull Request”
14. Keep base:main, and in compare:, choose the branch that you have been working on and create the Pull Request.

Your pull request will remain open until other people review it and accept that pull request which essentially takes all your work from your branch and adds it into the “main” branch.

Everyone will work like this and at the end the “main” branch will be our finished project.

---

## 9. Help

ASK ME, CHARLIE, LEO, OR CHATGPT/CLAUDE FOR QUESTIONS! (edited)

---

## 10. Troubleshooting

!!! If you look through this checklist and follow the steps, but still are unable to download or run into some undocumented issues, reach out in the groupme.
