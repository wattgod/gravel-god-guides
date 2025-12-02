# GitHub Pages Setup Guide
## For gravel-god-guides Repository

This guide will walk you through setting up GitHub Pages for your gravel-god-guides repository in about 5 minutes.

---

## Step 1: Create the Repository on GitHub

1. Go to [github.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name:** `gravel-god-guides`
   - **Description:** (optional) "Gravel God Training Guides and Resources"
   - **Visibility:** Choose Public or Private (Public required for free GitHub Pages)
   - **DO NOT** initialize with README, .gitignore, or license (we'll add files manually)
5. Click **"Create repository"**

---

## Step 2: Upload Your Files

You have two options:

### Option A: Upload via Web Interface (Easiest)

1. On your new repository page, click **"uploading an existing file"** link
2. Drag and drop your entire `gravel-god-guides/` folder contents
3. Scroll down and enter a commit message: `"Initial commit: Add gravel god guides"`
4. Click **"Commit changes"**

### Option B: Upload via Git (Command Line)

If you have Git installed, you can use these commands:

```bash
# Navigate to your gravel-god-guides folder
cd /path/to/gravel-god-guides

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Add gravel god guides"

# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/gravel-god-guides.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 3: Enable GitHub Pages

1. In your repository, go to **Settings** (top menu bar)
2. Scroll down to **Pages** in the left sidebar
3. Under **Source**, select:
   - **Branch:** `main` (or `master` if that's your default branch)
   - **Folder:** `/ (root)`
4. Click **Save**

---

## Step 4: Access Your Site

1. GitHub will provide a URL like:
   ```
   https://YOUR_USERNAME.github.io/gravel-god-guides/
   ```
2. It may take 1-2 minutes for the site to be available
3. You'll see a green checkmark when it's live

---

## Step 5: Customize (Optional)

### Add a README.md

Create a `README.md` file in your repository root:

```markdown
# Gravel God Training Guides

Welcome to the Gravel God Training Guides repository.

## Contents

- Training guides and resources
- Workout templates
- Training philosophy documents

## Links

- [View Live Site](https://YOUR_USERNAME.github.io/gravel-god-guides/)
```

### Add an index.html

If you want a custom homepage, create an `index.html` file:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gravel God Training Guides</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 { color: #333; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <h1>🚴 Gravel God Training Guides</h1>
    <p>Welcome to the Gravel God Training Guides repository.</p>
    <!-- Add your content here -->
</body>
</html>
```

---

## Troubleshooting

### Site Not Loading?
- Wait 1-2 minutes after enabling Pages
- Check that your branch is set correctly in Settings > Pages
- Ensure you have at least one file in the repository

### Files Not Showing?
- Make sure files are in the root directory or properly linked
- Check file names for special characters (use hyphens instead of spaces)
- Verify file permissions

### Need to Update?
- Simply edit files in the repository and commit changes
- GitHub Pages will automatically rebuild (may take 1-2 minutes)

---

## Quick Checklist

- [ ] Created repository on GitHub
- [ ] Uploaded all files from gravel-god-guides folder
- [ ] Enabled GitHub Pages in Settings
- [ ] Selected main branch as source
- [ ] Verified site is live at YOUR_USERNAME.github.io/gravel-god-guides
- [ ] (Optional) Added README.md
- [ ] (Optional) Added index.html

---

## Next Steps

Once your site is live, you can:
- Share the URL with others
- Add more content by committing new files
- Customize the appearance with CSS
- Add navigation between pages

**That's it! Your GitHub Pages site should be live in about 5 minutes.** 🎉

