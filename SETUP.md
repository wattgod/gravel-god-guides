# Setup Instructions

## 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `gravel-god-guides`
3. Description: "Production-ready HTML training guide generator for Gravel God Cycling"
4. Choose: Private (recommended) or Public
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## 2. Connect Local Repository

After creating the GitHub repo, run:

```bash
cd ~/Documents/gravel-god-guides

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/gravel-god-guides.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/gravel-god-guides.git
```

## 3. Initial Commit & Push

```bash
git add .
git commit -m "Initial commit: Production-ready guide generator"
git branch -M main
git push -u origin main
```

## 4. Verify

Check that files are on GitHub:
- `generators/guide_generator.py`
- `race_data/unbound_gravel_200.json`
- `race_data/ayahuasca_beginner_template.json`
- `README.md`
- `.gitignore`

## 5. Test Generation

```bash
python generators/guide_generator.py \
  --race race_data/unbound_gravel_200.json \
  --plan race_data/ayahuasca_beginner_template.json \
  --output-dir output/

# Check output
ls -lh output/*.html
```

## Next Steps

- Add more race data files to `race_data/`
- Add more plan templates to `race_data/`
- Customize templates in `templates/` (if needed)
- Update documentation in `docs/`

