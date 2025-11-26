#!/bin/bash

# GitHub Repository Setup Script for Gravel God Guides
# This script will help you create and push to GitHub

set -e

REPO_NAME="gravel-god-guides"
GITHUB_USER=""

echo "🚴 Gravel God Guides - GitHub Setup"
echo "===================================="
echo ""

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI found"
    
    # Check if user is logged in
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI authenticated"
        GITHUB_USER=$(gh api user --jq .login)
        echo "   Logged in as: $GITHUB_USER"
        echo ""
        
        # Create repository
        echo "📦 Creating repository: $REPO_NAME"
        gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
        
        echo ""
        echo "✅ Repository created and pushed!"
        echo ""
        echo "🌐 Enabling GitHub Pages..."
        gh api repos/$GITHUB_USER/$REPO_NAME/pages -X POST -f source[branch]=main -f source[path]=/ || echo "Note: You may need to enable Pages manually in Settings"
        
        echo ""
        echo "🎉 Setup Complete!"
        echo ""
        echo "Your site will be available at:"
        echo "https://$GITHUB_USER.github.io/$REPO_NAME/"
        echo ""
        echo "It may take 1-2 minutes for GitHub Pages to activate."
        
    else
        echo "❌ Not logged in to GitHub CLI"
        echo ""
        echo "Please run: gh auth login"
        echo "Then run this script again."
        exit 1
    fi
    
else
    echo "⚠️  GitHub CLI not found"
    echo ""
    echo "Option 1: Install GitHub CLI"
    echo "  brew install gh"
    echo "  gh auth login"
    echo "  Then run this script again"
    echo ""
    echo "Option 2: Manual Setup"
    echo ""
    echo "1. Go to https://github.com/new"
    echo "2. Create a repository named: $REPO_NAME"
    echo "3. DO NOT initialize with README"
    echo "4. Then run these commands:"
    echo ""
    echo "   git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    echo "5. Go to Settings > Pages"
    echo "6. Select 'main' branch and '/' folder"
    echo "7. Click Save"
    echo ""
    echo "Your site will be at: https://YOUR_USERNAME.github.io/$REPO_NAME/"
    exit 1
fi

