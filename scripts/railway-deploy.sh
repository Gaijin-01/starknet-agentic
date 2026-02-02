#!/bin/bash
# Railway Agent Deployment Script
# Creates separate GitHub repos and pushes each agent

set -e

echo "🚂 Railway Agent Deployment Script"
echo "==================================="

# Configuration
REPOS=("ct-intelligence-agent-ts" "starknet-yield-agent-ts")
BASE_DIR="/home/wner/clawd/skills"

for REPO_NAME in "${REPOS[@]}"; do
    AGENT_DIR="$BASE_DIR/$REPO_NAME"
    
    echo ""
    echo "📦 Processing: $REPO_NAME"
    echo "   Path: $AGENT_DIR"
    
    # Check if directory exists
    if [ ! -d "$AGENT_DIR" ]; then
        echo "   ❌ Directory not found, skipping..."
        continue
    fi
    
    # Create GitHub repo (private by default)
    echo "   🔧 Creating GitHub repo..."
    gh repo create "$REPO_NAME" --private --description "Railway-deployable agent: $REPO_NAME" || {
        echo "   ⚠️  Repo may already exist, continuing..."
    }
    
    # Initialize git if needed
    if [ ! -d "$AGENT_DIR/.git" ]; then
        echo "   📝 Initializing git..."
        cd "$AGENT_DIR"
        git init
        git add -A
        git commit -m "Initial commit: $REPO_NAME"
    else
        echo "   🔄 Git already initialized, adding changes..."
        cd "$AGENT_DIR"
        git add -A
        git commit -m "Update: $(date +%Y-%m-%d)" || echo "   ℹ️  No changes to commit"
    fi
    
    # Add remote and push
    echo "   🔗 Adding remote and pushing..."
    git remote remove origin 2>/dev/null || true
    git remote add origin "https://github.com/Gaijin-01/$REPO_NAME.git"
    git push -u origin main || git push -u origin master
    
    echo "   ✅ $REPO_NAME deployed to GitHub!"
    echo "   🔗 https://github.com/Gaijin-01/$REPO_NAME"
done

echo ""
echo "🎉 All agents pushed to GitHub!"
echo ""
echo "Next steps:"
echo "1. Go to https://railway.com"
echo "2. Connect your GitHub account"
echo "3. New Project → Deploy from GitHub repo"
echo "4. Select: ct-intelligence-agent-ts"
echo "5. Select: starknet-yield-agent-ts"
echo ""
