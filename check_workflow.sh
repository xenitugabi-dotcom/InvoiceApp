#!/data/data/com.termux/files/usr/bin/bash

# ============================
# GitHub Actions Diagnostic Script
# ============================

echo "🔍 Starting GitHub Actions diagnostic..."

# 1️⃣ Check current directory
echo -e "\n1️⃣ Current directory:"
pwd

# 2️⃣ Check if inside a Git repo
echo -e "\n2️⃣ Checking Git repository..."
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "✅ Inside a Git repo"
else
    echo "❌ Not a Git repository"
    exit 1
fi

# 3️⃣ Check current branch
BRANCH=$(git branch --show-current)
echo -e "\n3️⃣ Current branch: $BRANCH"

# 4️⃣ Check remotes
echo -e "\n4️⃣ Git remotes:"
git remote -v

# 5️⃣ Check workflow folder
WORKFLOW_DIR="./.github/workflows"
echo -e "\n5️⃣ Checking workflow folder: $WORKFLOW_DIR"
if [ -d "$WORKFLOW_DIR" ]; then
    ls -l $WORKFLOW_DIR
else
    echo "❌ Workflow folder not found!"
fi

# 6️⃣ Check YAML syntax for each workflow file
echo -e "\n6️⃣ Checking YAML syntax..."
for file in $WORKFLOW_DIR/*.yml $WORKFLOW_DIR/*.yaml; do
    if [ -f "$file" ]; then
        echo -e "\n📝 Linting $file"
        if command -v yamllint >/dev/null 2>&1; then
            yamllint "$file"
        else
            echo "⚠️ yamllint not installed. Installing..."
            pip install --user yamllint
            yamllint "$file"
        fi
    fi
done

# 7️⃣ Show last commit
echo -e "\n7️⃣ Last commit info:"
git log -1 --oneline

# 8️⃣ Check if workflow file contains 'on: push' for current branch
echo -e "\n8️⃣ Checking workflow triggers..."
for file in $WORKFLOW_DIR/*.yml $WORKFLOW_DIR/*.yaml; do
    if [ -f "$file" ]; then
        echo -e "\n🔹 $file triggers:"
        grep -A2 "^on:" "$file"
    fi
done

# 9️⃣ Suggest pushing a dummy commit
echo -e "\n💡 Tip: If workflow still doesn’t run, try pushing a dummy commit:"
echo '   echo "# trigger $(date)" >> trigger.txt; git add trigger.txt; git commit -m "Trigger Actions"; git push origin '"$BRANCH"

echo -e "\n✅ Diagnostic complete!"