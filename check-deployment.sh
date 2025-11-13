#!/bin/bash
# Pre-deployment checklist script for ACL Guardian

echo "🔍 ACL GUARDIAN - PRE-DEPLOYMENT CHECKS"
echo "========================================"
echo ""

# Check if Git is initialized
if [ -d .git ]; then
    echo "✅ Git repository initialized"
else
    echo "❌ Git not initialized - Run: git init"
fi

# Check if .env files exist
if [ -f backend/.env ]; then
    echo "✅ Backend .env exists"
    echo "⚠️  WARNING: Make sure .env is in .gitignore!"
else
    echo "⚠️  Backend .env not found"
fi

# Check if .gitignore exists
if [ -f .gitignore ]; then
    echo "✅ .gitignore exists"
else
    echo "❌ .gitignore missing"
fi

# Check required backend files
echo ""
echo "📦 Checking Backend Files..."
[ -f backend/requirements.txt ] && echo "✅ requirements.txt" || echo "❌ requirements.txt missing"
[ -f backend/main.py ] && echo "✅ main.py" || echo "❌ main.py missing"
[ -f backend/render.yaml ] && echo "✅ render.yaml" || echo "❌ render.yaml missing"

# Check required frontend files
echo ""
echo "🌐 Checking Frontend Files..."
[ -f package.json ] && echo "✅ package.json" || echo "❌ package.json missing"
[ -f next.config.ts ] && echo "✅ next.config.ts" || echo "❌ next.config.ts missing"
[ -f vercel.json ] && echo "✅ vercel.json" || echo "❌ vercel.json missing"

echo ""
echo "📝 Required Environment Variables for Deployment:"
echo ""
echo "RENDER (Backend):"
echo "  - PYTHON_VERSION"
echo "  - FRONTEND_URL"
echo "  - FITBIT_CLIENT_ID"
echo "  - FITBIT_CLIENT_SECRET"
echo "  - ENCRYPTION_KEY"
echo "  - SUPABASE_URL"
echo "  - SUPABASE_KEY"
echo "  - SUPABASE_ANON_KEY"
echo ""
echo "VERCEL (Frontend):"
echo "  - NEXT_PUBLIC_API_URL"
echo ""
echo "✨ Ready to deploy! Follow DEPLOYMENT_GUIDE.md"
