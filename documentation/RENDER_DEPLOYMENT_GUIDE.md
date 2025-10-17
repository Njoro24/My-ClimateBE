# Climate Witness Chain - Render Deployment Guide

## 🚀 Deploy to Render

### **Prerequisites:**
1. GitHub repository with your code
2. Render account (free tier available)
3. Code pushed to GitHub

### **Step 1: Prepare Your Repository**

Make sure these files are in your BECW directory:
- ✅ `render_start.py` - Startup script
- ✅ `render_requirements.txt` - Dependencies
- ✅ `render_build.sh` - Build script
- ✅ `Dockerfile` - Container configuration
- ✅ `render.yaml` - Render configuration

### **Step 2: Deploy on Render**

#### **Option A: Using Render Dashboard (Recommended)**

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub Repository**:
   - Select your repository
   - Choose the branch (usually `main` or `master`)
4. **Configure Service**:
   ```
   Name: climate-witness-backend
   Environment: Python 3
   Build Command: ./render_build.sh
   Start Command: python render_start.py
   ```

#### **Option B: Using render.yaml (Auto-deploy)**

1. **Push render.yaml** to your repository root
2. **Go to Render Dashboard**
3. **Click "New +"** → **"Blueprint"**
4. **Connect Repository** and Render will auto-configure

### **Step 3: Environment Variables**

Add these in Render Dashboard → Your Service → Environment:

#### **Required Variables:**
```bash
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=10000
SECRET_KEY=your_secret_key_here_change_this
DATABASE_URL=sqlite:///./climate_witness.db
CORS_ORIGINS=https://your-frontend-domain.com
```

#### **Optional Variables (add if you have credentials):**
```bash
# M-Pesa (if you have credentials)
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_BUSINESS_SHORT_CODE=174379
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://your-app-name.onrender.com/api/payments/mpesa/callback
MPESA_ENVIRONMENT=sandbox

# Twilio SMS (if you have credentials)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_phone_number

# AI Services (if you have keys)
ANTHROPIC_API_KEY=your_anthropic_key
```

### **Step 4: Deployment Process**

1. **Push Code** to GitHub
2. **Render Auto-deploys** (takes 2-5 minutes)
3. **Check Logs** in Render Dashboard
4. **Test Health Check**: `https://your-app-name.onrender.com/health`

### **Step 5: Update Frontend**

Update your frontend `.env` file:
```bash
VITE_API_BASE_URL=https://your-app-name.onrender.com
```

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. Build Fails**
```bash
# Check render_requirements.txt
# Remove problematic packages like hyperon if needed
# Ensure all dependencies are compatible
```

#### **2. App Crashes on Start**
```bash
# Check Render logs
# Verify environment variables
# Ensure DATABASE_URL is set correctly
```

#### **3. Database Issues**
```bash
# SQLite works on Render free tier
# Database is created automatically on first run
# Check file permissions in logs
```

#### **4. CORS Errors**
```bash
# Update CORS_ORIGINS with your frontend domain
# Format: https://your-frontend.netlify.app,https://your-domain.com
```

### **Render Logs Commands:**
```bash
# View logs in Render Dashboard
# Or use Render CLI:
render logs -s your-service-name
```

## 📊 **Monitoring**

### **Health Checks:**
- **Health Endpoint**: `/health`
- **API Docs**: `/docs`
- **Admin Stats**: `/api/admin/dashboard/stats` (requires auth)

### **Performance:**
- **Free Tier**: 512MB RAM, sleeps after 15min inactivity
- **Paid Tier**: More resources, no sleep

## 🎯 **Post-Deployment**

### **1. Test API Endpoints:**
```bash
# Health check
curl https://your-app-name.onrender.com/health

# API documentation
https://your-app-name.onrender.com/docs
```

### **2. Create Admin User:**
The app creates sample users automatically, including:
- **Admin**: admin@climatewitness.com / admin123

### **3. Update Frontend:**
Update your frontend to use the new API URL:
```javascript
// In your frontend .env
VITE_API_BASE_URL=https://your-app-name.onrender.com
```

## 🔐 **Security Notes**

1. **Change SECRET_KEY** in production
2. **Use HTTPS** (Render provides this automatically)
3. **Set proper CORS_ORIGINS**
4. **Don't commit sensitive data** to GitHub
5. **Use Render environment variables** for secrets

## 💡 **Tips for Success**

1. **Start Simple**: Deploy with minimal dependencies first
2. **Check Logs**: Always check Render logs if something fails
3. **Test Locally**: Ensure `python render_start.py` works locally
4. **Use SQLite**: Works well on Render free tier
5. **Monitor Usage**: Free tier has limits, upgrade if needed

## 🆘 **Support**

If deployment fails:
1. Check Render build logs
2. Verify all files are committed to GitHub
3. Ensure environment variables are set
4. Test the startup script locally
5. Check Render documentation: https://render.com/docs

**Your Climate Witness Chain backend will be live at:**
`https://your-app-name.onrender.com` 🎉