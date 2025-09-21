# 🔐 Render Environment Variables for Climate Witness Chain

## 🚀 **Required Environment Variables**

Copy and paste these into your Render Dashboard → Your Service → Environment:

### **Core Application Settings:**
```bash
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=10000
```

### **Security (CRITICAL):**
```bash
SECRET_KEY=CWC_f317b630327c04593af918c3fd1ab2fc807b96c8c37002d5_PROD
```

### **Database:**
```bash
DATABASE_URL=sqlite:///./climate_witness.db
```

### **CORS (Update with your frontend domain):**
```bash
CORS_ORIGINS=https://your-frontend-domain.com,https://your-app.netlify.app
```

### **Application Configuration:**
```bash
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### **File Upload:**
```bash
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=jpg,jpeg,png,gif,pdf,doc,docx
UPLOAD_FOLDER=uploads
```

### **Payment Configuration:**
```bash
PAYMENT_CURRENCY=KES
MIN_PAYMENT_AMOUNT=1.0
MAX_PAYMENT_AMOUNT=70000.0
```

## 🔧 **Optional Environment Variables**

Add these only if you have the credentials:

### **M-Pesa Integration (Optional):**
```bash
MPESA_CONSUMER_KEY=your_mpesa_consumer_key
MPESA_CONSUMER_SECRET=your_mpesa_consumer_secret
MPESA_BUSINESS_SHORT_CODE=174379
MPESA_PASSKEY=your_mpesa_passkey
MPESA_CALLBACK_URL=https://your-app-name.onrender.com/api/payments/mpesa/callback
MPESA_ENVIRONMENT=sandbox
```

### **SMS/Twilio Integration (Optional):**
```bash
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

### **AI Services (Optional):**
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### **Blockchain (Optional):**
```bash
POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com/
PRIVATE_KEY=your_blockchain_private_key
```

## 📋 **How to Add Environment Variables in Render:**

### **Step 1: Go to Render Dashboard**
1. Navigate to https://dashboard.render.com/
2. Click on your Climate Witness service
3. Go to the **"Environment"** tab

### **Step 2: Add Variables**
1. Click **"Add Environment Variable"**
2. Enter **Key** and **Value** for each variable
3. Click **"Save Changes"**

### **Step 3: Redeploy**
Render will automatically redeploy when you save environment variables.

## 🛡️ **Security Best Practices:**

### **✅ DO:**
- Use the generated SECRET_KEY exactly as provided
- Keep different keys for different environments (dev/staging/prod)
- Store sensitive data only in Render environment variables
- Update CORS_ORIGINS with your actual frontend domain

### **❌ DON'T:**
- Never commit secret keys to GitHub
- Don't use simple or predictable secret keys
- Don't share secret keys in chat or email
- Don't use the same key across multiple projects

## 🔄 **Environment Variable Priority:**

Render environment variables override any values in your code or .env files:
```
Render Environment Variables > .env files > Default values in code
```

## 🧪 **Testing Your Configuration:**

After setting environment variables, test your deployment:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Should return: {"status":"healthy"}
```

## 🆘 **Troubleshooting:**

### **If SECRET_KEY is wrong:**
- App will fail to start
- Check Render logs for "Invalid secret key" errors
- Regenerate key using `python generate_secret_key.py`

### **If CORS_ORIGINS is wrong:**
- Frontend will get CORS errors
- Update with your actual frontend domain
- Format: `https://domain1.com,https://domain2.com`

### **If DATABASE_URL is wrong:**
- Database operations will fail
- Use: `sqlite:///./climate_witness.db` for SQLite
- Or use Render's PostgreSQL add-on URL

## 🎯 **Quick Copy-Paste for Render:**

**Minimum required variables for basic functionality:**
```
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=10000
SECRET_KEY=CWC_f317b630327c04593af918c3fd1ab2fc807b96c8c37002d5_PROD
DATABASE_URL=sqlite:///./climate_witness.db
CORS_ORIGINS=https://your-frontend-domain.com
PAYMENT_CURRENCY=KES
MIN_PAYMENT_AMOUNT=1.0
MAX_PAYMENT_AMOUNT=70000.0
```

**Your Climate Witness Chain backend will be secure and ready for production!** 🚀