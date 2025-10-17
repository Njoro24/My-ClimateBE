# 🔗 Frontend Connection Fix Guide

## 🔧 **Issue Fixed: Network Error During Login**

The frontend was trying to connect to `http://localhost:8000` instead of your Railway deployment URL.

## ✅ **Solution Applied:**

### **1. Updated Backend (simple_main.py)**
- ✅ **Fixed login endpoint** - Now returns proper `access_token`, `refresh_token`, and `user` data
- ✅ **Added auth endpoints** - `/refresh`, `/me`, `/logout` for complete auth flow
- ✅ **Proper CORS** - Allows frontend connections
- ✅ **Request models** - Handles login and payment requests correctly

### **2. Updated Frontend Environment**
- ✅ **Created `.env.production`** - Production environment file
- ✅ **Updated `.env`** - Placeholder for Railway URL

## 🚀 **Fix Your Frontend Connection:**

### **Step 1: Get Your Railway URL**
1. Go to your Railway dashboard
2. Find your deployed app
3. Copy the domain (e.g., `https://your-app-name.up.railway.app`)

### **Step 2: Update Frontend Environment**
Replace `your-railway-app-name` with your actual Railway domain:

**In `FECW/ClimateWitness/.env`:**
```bash
VITE_API_BASE_URL=https://your-actual-railway-domain.up.railway.app
```

**Example:**
```bash
VITE_API_BASE_URL=https://climate-witness-production.up.railway.app
```

### **Step 3: Test the Connection**
```bash
# Test your Railway backend directly
curl https://your-railway-domain.up.railway.app/health

# Should return:
{
  "status": "healthy",
  "service": "climate_witness_api",
  "environment": "production"
}
```

### **Step 4: Test Login Endpoint**
```bash
curl -X POST https://your-railway-domain.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Should return:
{
  "access_token": "access_demo_user_1234567890_abcd1234",
  "refresh_token": "refresh_demo_user_1234567890_efgh5678",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "full_name": "Demo User",
    "role": "user",
    "is_active": true,
    "is_verified": true
  },
  "message": "Login successful"
}
```

### **Step 5: Restart Frontend Development Server**
```bash
cd FECW/ClimateWitness
npm run dev
```

## 🎯 **Expected Results:**

### **✅ Login Should Work Now:**
1. **Frontend loads** without errors
2. **Login form appears** 
3. **Enter any email/password** (demo mode accepts anything)
4. **Login succeeds** and you see the dashboard
5. **No more "Network error"** messages

### **✅ Test Credentials (Demo Mode):**
- **Email**: Any email (e.g., `test@example.com`)
- **Password**: Any password (e.g., `test123`)
- **Result**: Should login successfully

## 🛠️ **Troubleshooting:**

### **Still Getting Network Error?**

#### **1. Check Railway URL:**
```bash
# Make sure your Railway app is running
curl https://your-railway-domain.up.railway.app/health
```

#### **2. Check CORS:**
```bash
# Test CORS from browser console
fetch('https://your-railway-domain.up.railway.app/health')
  .then(r => r.json())
  .then(console.log)
```

#### **3. Check Frontend Environment:**
```bash
# In browser console, check the API URL
console.log(import.meta.env.VITE_API_BASE_URL)
```

#### **4. Check Network Tab:**
- Open browser DevTools → Network tab
- Try to login
- Look for the actual request URL
- Check if it's going to Railway or localhost

### **Common Issues & Fixes:**

#### **Issue: Still connecting to localhost**
```bash
# Fix: Update .env file with correct Railway URL
VITE_API_BASE_URL=https://your-actual-railway-domain.up.railway.app
```

#### **Issue: CORS error**
```bash
# Fix: Update Railway CORS_ORIGINS environment variable
CORS_ORIGINS=https://localhost:3000,https://localhost:5173,https://your-frontend-domain.com
```

#### **Issue: 404 on login**
```bash
# Fix: Check if Railway is using simple_main:app
APP_MODULE=simple_main:app
```

## 🎉 **Success Indicators:**

- ✅ **Health check works**: `curl https://your-railway-domain.up.railway.app/health`
- ✅ **Login endpoint works**: Returns proper tokens and user data
- ✅ **Frontend connects**: No network errors in browser console
- ✅ **Login succeeds**: Can login with any credentials (demo mode)
- ✅ **Dashboard loads**: See the Climate Witness Chain interface

## 🔄 **Quick Test Commands:**

```bash
# 1. Test Railway backend
curl https://your-railway-domain.up.railway.app/health

# 2. Test login endpoint
curl -X POST https://your-railway-domain.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test"}'

# 3. Check frontend environment
cd FECW/ClimateWitness
cat .env | grep VITE_API_BASE_URL

# 4. Restart frontend
npm run dev
```

## 🚀 **Next Steps After Login Works:**

1. **Test payment flow** - Try the donation button
2. **Upgrade to full backend** - Change `APP_MODULE=main:app` in Railway
3. **Add real authentication** - Replace demo login with real auth
4. **Deploy frontend** - Deploy frontend to Vercel/Netlify
5. **Add production features** - Enable real M-Pesa, SMS, etc.

**Your frontend should connect to Railway successfully now!** 🔗✅

---

## 📞 **Need Help?**

If you're still getting network errors:
1. **Share your Railway URL** - So I can help test it
2. **Check browser console** - Look for specific error messages
3. **Test with curl** - Verify backend is responding
4. **Check environment variables** - Both Railway and frontend

**The connection should work perfectly now!** 🚀