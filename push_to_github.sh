#!/bin/bash
# Script to push GeoJSON Creation Tool to GitHub

echo "🚀 Pushing GeoJSON Creation Tool to GitHub..."
echo ""
echo "Make sure you've created the repository on GitHub first!"
echo "Repository name: GeoJSON-Creation-Tool"
echo ""
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username is required"
    exit 1
fi

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "⚠️  Remote 'origin' already exists. Updating..."
    git remote set-url origin https://github.com/$GITHUB_USERNAME/GeoJSON-Creation-Tool.git
else
    echo "➕ Adding remote origin..."
    git remote add origin https://github.com/$GITHUB_USERNAME/GeoJSON-Creation-Tool.git
fi

echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "🌐 View your repository at: https://github.com/$GITHUB_USERNAME/GeoJSON-Creation-Tool"
else
    echo ""
    echo "❌ Push failed. Make sure:"
    echo "   1. The repository exists on GitHub"
    echo "   2. You have permission to push"
    echo "   3. You're authenticated (use 'gh auth login' if using GitHub CLI)"
fi
