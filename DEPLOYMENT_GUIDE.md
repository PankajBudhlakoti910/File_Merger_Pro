# 🚀 Vercel Deployment Guide for File Merger Pro

This guide walks you through deploying File Merger Pro to Vercel for a live public URL.

## ✅ Prerequisites

1. ✅ GitHub account with the repository pushed
2. ✅ Vercel account (free tier available)
3. ✅ Project converted to Flask (already done!)

## 📋 Step-by-Step Deployment

### Step 1: Commit Your Changes to GitHub

```bash
cd /workspaces/File_Merger_Pro

# Stage all changes
git add .

# Commit with a message
git commit -m "Convert to Flask and add Vercel deployment config"

# Push to GitHub
git push origin main
```

### Step 2: Create Vercel Account

1. Go to [https://vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. **Select "Continue with GitHub"**
4. Authorize Vercel to access your GitHub account
5. Choose your GitHub account/organization

### Step 3: Import Your Repository

1. Once logged in, click **"New Project"** or **"Add New..."**
2. Under "Import Git Repository", search for **"File_Merger_Pro"**
3. Click **"Import"**

### Step 4: Configure Project Settings

Vercel should auto-detect the Python project. Verify:

- **Framework:** Leave as "Other" (for custom Python)
- **Build Command:** `pip install -r requirements.txt` (should be auto-filled)
- **Output Directory:** `.` (dot)
- **Install Command:** Default (blank)

### Step 5: Environment Variables (Optional)

No environment variables are required for basic functionality. Skip this section unless you need to add custom variables.

### Step 6: Deploy!

Click the **"Deploy"** button and wait for the deployment to complete.

### Step 7: Get Your Live URL

After successful deployment, Vercel will show you:

```
✅ Production: https://file-merger-pro.vercel.app
```

Your app is now **live and accessible to anyone!**

## 🔄 Automatic Deployments

After this initial setup:

1. **Any push to GitHub** automatically triggers a deployment
2. **Every commit** updates your live URL
3. **No manual steps required** - Vercel watches your repo!

### Example Workflow:

```bash
# Make changes locally
nano api/app.py

# Commit and push
git add api/app.py
git commit -m "Fix merge logic"
git push origin main

# ✅ Automatic deployment starts in Vercel!
# Check status: https://vercel.com/dashboard
```

## 📊 Monitor Your Deployment

### View Deployment Status

1. Go to [https://vercel.com/dashboard](https://vercel.com/dashboard)
2. Click on "File_Merger_Pro" project
3. See all deployments with timestamps and status

### View Logs

```bash
# Install Vercel CLI
npm install -g vercel

# View logs
vercel logs

# View specific deployment logs
vercel logs [URL]
```

## 🐛 Troubleshooting

### Issue: "Build failed"

**Check:**
- All requirements are in `requirements.txt`
- No typos in `vercel.json`
- `api/app.py` is valid Python

**Fix:**
```bash
# Test locally first
python -m pip install -r requirements.txt
python api/app.py
```

### Issue: "500 Error on live site"

**Check logs:**
1. Go to Vercel dashboard
2. Click project → Deployments
3. Click the failed deployment
4. Check "Functions" tab for errors

### Issue: "Cannot find module"

**Add to `requirements.txt`:**
```txt
flask>=2.3.0
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.0.0
werkzeug>=2.3.0
```

Then:
```bash
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

## 📈 Performance Tips

1. **Optimize file uploads** - Set reasonable file size limits
2. **Cache merged data** - Store in-memory for faster downloads
3. **Monitor usage** - Vercel dashboard shows function invocations

## 🔒 Security Notes

1. **No sensitive data** should be in code
2. **Use environment variables** for secrets
3. **Validate all inputs** (already done in code)
4. **Monitor logs** for suspicious activity

## 📱 Test Your Live App

1. Share the URL: `https://file-merger-pro.vercel.app`
2. Test file uploads, merge, and download
3. Try on mobile too!

## 🎯 Next Steps

- ✅ **Tell users about the live link**
- ✅ **Add to portfolio/resume**
- ✅ **Monitor Vercel dashboard**
- ✅ **Make improvements and auto-deploy**

## 📚 Additional Resources

- [Vercel Docs](https://vercel.com/docs)
- [Flask on Vercel](https://vercel.com/docs/concepts/functions/serverless-functions)
- [Python Support](https://vercel.com/docs/concepts/frameworks/python)

---

**Your app is now live! 🎉**

For questions, check Vercel's documentation or GitHub issues.
