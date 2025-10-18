# Climate Witness Chain - Deployment Guide

## 🚀 Quick Deployment Steps

### Backend Deployment to Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up/login with GitHub

2. **Deploy Backend**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `BECW` folder as root directory
   - Configure:
     - **Name**: `climate-witness-api`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python main.py`
     - **Instance Type**: Free (for testing) or Starter ($7/month)

3. **Environment Variables**
   ```
   PORT=8000
   DATABASE_URL=sqlite:///./climate_witness.db
   SECRET_KEY=your-secret-key-here
   ENVIRONMENT=production
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note your Render URL: `https://your-app-name.onrender.com`

### Frontend Deployment to Netlify

1. **Update API URL**
   - Copy your Render URL from above
   - Update `netlify.toml`:
   ```toml
   [context.production.environment]
   VITE_API_URL = "https://your-render-app.onrender.com"
   ```

2. **Deploy to Netlify**
   - Go to [netlify.com](https://netlify.com)
   - Sign up/login with GitHub
   - Click "Add new site" → "Import an existing project"
   - Connect GitHub and select your repository
   - Configure:
     - **Base directory**: `FECW/ClimateWitness`
     - **Build command**: `npm run build`
     - **Publish directory**: `FECW/ClimateWitness/dist`

3. **Environment Variables in Netlify**
   - Go to Site settings → Environment variables
   - Add:
   ```
   VITE_API_URL=https://your-render-app.onrender.com
   ```

4. **Deploy**
   - Click "Deploy site"
   - Wait for build (3-5 minutes)
   - Your site will be live at: `https://random-name.netlify.app`

## 🔧 Enhanced Functions Status

### ✅ Function 1: Decentralized News & Media Integrity
**Location**: `BECW/app/api/routes/media_integrity.py`

**Enhanced Features**:
- ✅ Real EXIF metadata extraction from uploaded images
- ✅ GPS coordinate validation against verified climate events
- ✅ User trust score integration from actual database
- ✅ Cross-reference with verified climate events within 50km radius
- ✅ Misinformation detection using real event contradictions
- ✅ Community fact-checking with weighted expert/citizen consensus

**API Endpoints**:
- `POST /api/media-integrity/verify-media` - Verify media authenticity
- `POST /api/media-integrity/detect-misinformation` - Detect climate misinformation
- `POST /api/media-integrity/community-fact-check` - Community-based fact checking
- `POST /api/media-integrity/upload-media` - Upload and verify media files

### ✅ Function 2: Explainable AI for Civic Decision-Making
**Location**: `BECW/app/api/routes/civic_decision_making.py`

**Enhanced Features**:
- ✅ Real climate data analysis using verified events database
- ✅ Policy effectiveness prediction based on historical outcomes
- ✅ Multi-level explanations (citizen, expert, policymaker)
- ✅ Democratic participation quality assessment
- ✅ Resource allocation optimization using real economic impact data
- ✅ AI-assisted policy recommendations with similar case analysis

**API Endpoints**:
- `POST /api/civic-decisions/democratic-decision` - Make democratic decisions
- `POST /api/civic-decisions/predict-policy-impact` - Predict policy outcomes
- `POST /api/civic-decisions/allocate-resources` - Optimize resource allocation
- `POST /api/civic-decisions/ai-policy-recommendation` - AI policy suggestions

## 📊 Real Data Integration

### Database Schema
The functions use real data from SQLite database:

```sql
-- Users with real trust scores
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    trust_score INTEGER DEFAULT 50,
    verification_count INTEGER DEFAULT 0,
    location_region TEXT
);

-- Verified climate events with GPS and economic impact
CREATE TABLE events (
    id TEXT PRIMARY KEY,
    event_type TEXT,
    location TEXT,
    latitude REAL,
    longitude REAL,
    timestamp DATETIME,
    description TEXT,
    verification_status TEXT DEFAULT 'pending',
    economic_impact REAL,
    user_id TEXT
);
```

### Enhanced MeTTa Knowledge Base
**Location**: `BECW/metta/enhanced_real_data.metta`

**Features**:
- Real climate pattern recognition
- Enhanced trust score calculation with network effects
- Economic impact analysis using verified data
- Democratic participation quality assessment
- Multi-audience explanation generation

## 🎯 Function Demonstrations

### Media Integrity Function Demo

```bash
# Test authentic media verification
curl -X POST "https://your-render-app.onrender.com/api/media-integrity/verify-media" \
  -H "Content-Type: application/json" \
  -d '{
    "media_type": "photo",
    "source": "amina@example.com",
    "metadata": {
      "GPS": [3.1167, 35.6167],
      "DateTime": "2024-01-15 14:30:00",
      "Make": "Samsung",
      "Model": "Galaxy S21"
    },
    "claims": ["Severe drought in Turkana County"]
  }'

# Expected Response:
{
  "success": true,
  "authenticity_result": {
    "is_authentic": true,
    "overall_score": 0.89,
    "confidence_level": "high"
  },
  "verification_breakdown": {
    "metadata_integrity": 0.85,
    "source_credibility": 0.85,
    "technical_authenticity": 0.92
  },
  "explanation": {
    "methodology": "Multi-factor authenticity verification using metadata analysis, source validation, and technical checks"
  }
}
```

### Civic Decision-Making Function Demo

```bash
# Test policy impact prediction
curl -X POST "https://your-render-app.onrender.com/api/civic-decisions/predict-policy-impact" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "Establish community water storage and drought-resistant crop program",
    "location": "Turkana County",
    "timeframe": "5_years"
  }'

# Expected Response:
{
  "success": true,
  "impact_prediction": {
    "effectiveness_score": 0.78,
    "cost_benefit_ratio": 2.1,
    "risk_reduction_percentage": 30.0,
    "community_acceptance": 0.85
  },
  "analysis_details": {
    "historical_events_analyzed": 8,
    "economic_baseline": 165000,
    "vulnerability_factors": {...}
  }
}
```

## 🔍 Testing the Deployment

### Backend Health Check
```bash
curl https://your-render-app.onrender.com/health
# Should return: {"status": "healthy"}
```

### Frontend Access
1. Open your Netlify URL in browser
2. Navigate to "Media Integrity" page
3. Upload a test image
4. Navigate to "Civic Decision Making" page
5. Test policy impact prediction

### API Integration Test
1. Open browser developer tools
2. Check Network tab for API calls
3. Verify calls go to your Render backend URL
4. Check for successful responses (200 status)

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Backend already has CORS configured for all origins
   - Check if API URL is correct in frontend

2. **Build Failures**
   - **Render**: Check build logs, ensure all dependencies in requirements.txt
   - **Netlify**: Check build logs, ensure Node.js version compatibility

3. **Database Issues**
   - SQLite database is created automatically on first run
   - Check Render logs for database initialization messages

4. **API Connection Issues**
   - Verify VITE_API_URL environment variable
   - Check if Render service is running (not sleeping)

### Logs Access
- **Render**: Dashboard → Your Service → Logs
- **Netlify**: Site Dashboard → Functions → View logs

## 🎉 Success Verification

Your deployment is successful when:

1. ✅ Backend health endpoint returns "healthy"
2. ✅ Frontend loads without errors
3. ✅ Media integrity function accepts file uploads
4. ✅ Civic decision-making function shows policy predictions
5. ✅ API calls in browser network tab show 200 responses
6. ✅ Database operations work (user registration, event submission)

## 📈 Next Steps After Deployment

1. **Custom Domain**: Add your own domain to Netlify
2. **SSL Certificate**: Automatically provided by both platforms
3. **Monitoring**: Set up uptime monitoring
4. **Analytics**: Add Google Analytics or similar
5. **Performance**: Monitor API response times
6. **Scaling**: Upgrade to paid plans for production traffic

Your Climate Witness Chain application is now live and ready for real-world use! 🌍