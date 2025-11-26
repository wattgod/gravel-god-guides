# Quick GitHub Setup - Run These Commands

Since I can't directly access your GitHub account, here's the fastest way to get everything set up:

## Option 1: Using GitHub CLI (Recommended - Fastest)

```bash
# Install GitHub CLI (if not already installed)
brew install gh

# Authenticate
gh auth login

# Navigate to the folder
cd /Users/mattirowe/Downloads/gravel-god-guides

# Create repo and push (this does everything!)
gh repo create gravel-god-guides --public --source=. --remote=origin --push

# Enable GitHub Pages
gh api repos/wattgod/gravel-god-guides/pages -X POST -f source[branch]=main -f source[path]=/

# Done! Your site will be at:
# https://wattgod.github.io/gravel-god-guides/
```

## Option 2: Manual Web Interface (5 minutes)

1. **Create Repository:**
   - Go to https://github.com/new
   - Repository name: `gravel-god-guides`
   - Make it Public
   - **DO NOT** check "Add a README file"
   - Click "Create repository"

2. **Push Your Code:**
   ```bash
   cd /Users/mattirowe/Downloads/gravel-god-guides
   git remote add origin https://github.com/wattgod/gravel-god-guides.git
   git branch -M main
   git push -u origin main
   ```

3. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Click **Settings** (top menu)
   - Click **Pages** (left sidebar)
   - Under "Source", select:
     - Branch: `main`
     - Folder: `/ (root)`
   - Click **Save**

4. **Your site will be live at:**
   ```
   https://wattgod.github.io/gravel-god-guides/
   ```

## Option 3: Use the Automated Script

```bash
cd /Users/mattirowe/Downloads/gravel-god-guides
./setup-github.sh
```

The script will guide you through the process.

---

**Everything is ready to go!** All files are organized, git is initialized, and you just need to push to GitHub.

