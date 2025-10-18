# 🔧 CIVIC DECISION MAKING - TROUBLESHOOTING GUIDE

## 🚨 COMMON ISSUES & SOLUTIONS

### ❌ **Issue 1: "Predict Impact" Button Not Working**

#### **Symptoms:**
- Button shows "Analyzing..." but never completes
- Error messages in browser console
- No results displayed

#### **Solutions:**

1. **Check Backend Server:**
```bash
cd BECW
python simple_main.py
# Should show: "Server running on http://localhost:8000"
```

2. **Test API Connection:**
```bash
cd BECW
python test_civic_api.py
# Should show all tests passing
```

3. **Check Browser Console:**
- Press F12 → Console tab
- Look for error messages
- Common errors and fixes:

```javascript
// Error: "Failed to fetch"
// Solution: Backend server not running

// Error: "CORS policy"  
// Solution: Add CORS headers to backend

// Error: "Network request failed"
// Solution: Check API URL in config
```

4. **Verify API Configuration:**
```javascript
// In FECW/ClimateWitness/src/config/api.js
const API_BASE_URL = 'http://localhost:8000';  // For local development
// OR
const API_BASE_URL = 'https://your-deployed-url.com';  // For production
```

---

### ❌ **Issue 2: "Resource Allocation" Shows No Results**

#### **Symptoms:**
- "Optimize Resource Allocation" button doesn't respond
- Empty results or error messages

#### **Solutions:**

1. **Check Database Connection:**
```bash
cd BECW
python -c "
import sqlite3
conn = sqlite3.connect('climate_witness.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM events')
print(f'Events in database: {cursor.fetchone()[0]}')
conn.close()
"
```

2. **Initialize Database if Empty:**
```bash
cd BECW
python init_db.py
# This creates the database with sample data
```

3. **Test Resource Allocation Directly:**
```bash
cd BECW
python -c "
import requests
response = requests.post('http://localhost:8000/api/civic-decision-making/allocate-resources', 
    json={'available_resources': {'funding': 1000000, 'personnel': 50, 'equipment': 25}, 
          'community_needs': [], 'verified_impacts': []})
print(response.status_code, response.json())
"
```

---

### ❌ **Issue 3: "Build Consensus" Not Working**

#### **Symptoms:**
- Consensus building process doesn't start
- No stakeholder analysis shown

#### **Solutions:**

1. **Check Stakeholder Data:**
```javascript
// In browser console, check if policy data is loaded:
console.log(samplePolicies);
// Should show array of policy objects
```

2. **Verify API Endpoint:**
```bash
curl -X POST http://localhost:8000/api/civic-decision-making/build-consensus \
  -H "Content-Type: application/json" \
  -d '{"issue": "Test Policy", "participants": [], "positions": [], "evidence": []}'
```

3. **Check for Missing Dependencies:**
```bash
cd BECW
pip install -r requirements.txt
# Make sure all packages are installed
```

---

### ❌ **Issue 4: Frontend Not Connecting to Backend**

#### **Symptoms:**
- All buttons show loading but never complete
- Network errors in browser console

#### **Solutions:**

1. **Check Both Servers Running:**
```bash
# Terminal 1 - Backend
cd BECW
python simple_main.py
# Should show: Server running on http://localhost:8000

# Terminal 2 - Frontend  
cd FECW/ClimateWitness
npm run dev
# Should show: Local: http://localhost:5173
```

2. **Verify Environment Variables:**
```bash
# In FECW/ClimateWitness/.env
VITE_API_URL=http://localhost:8000
```

3. **Test Direct API Access:**
```bash
# Open browser and go to:
http://localhost:8000/docs
# Should show FastAPI documentation
```

---

### ❌ **Issue 5: Database Errors**

#### **Symptoms:**
- "Database connection failed" errors
- No historical data for analysis

#### **Solutions:**

1. **Check Database File:**
```bash
cd BECW
ls -la climate_witness.db
# Should show database file exists
```

2. **Recreate Database:**
```bash
cd BECW
rm climate_witness.db  # Remove old database
python init_db.py      # Create new database
python test_real_features.py  # Add sample data
```

3. **Verify Database Schema:**
```bash
cd BECW
python -c "
import sqlite3
conn = sqlite3.connect('climate_witness.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])
conn.close()
"
```

---

## 🚀 QUICK FIX CHECKLIST

### ✅ **Before Demo/Competition:**

1. **Backend Server:**
   - [ ] `cd BECW && python simple_main.py` 
   - [ ] Server shows "Running on http://localhost:8000"
   - [ ] No error messages in terminal

2. **Frontend Server:**
   - [ ] `cd FECW/ClimateWitness && npm run dev`
   - [ ] Shows "Local: http://localhost:5173"
   - [ ] No compilation errors

3. **API Tests:**
   - [ ] `cd BECW && python test_civic_api.py`
   - [ ] All 4 tests pass
   - [ ] No connection errors

4. **Database:**
   - [ ] `climate_witness.db` file exists in BECW folder
   - [ ] Contains sample events and users
   - [ ] No corruption errors

5. **Browser Test:**
   - [ ] Go to http://localhost:5173
   - [ ] Navigate to "Civic Decision Making"
   - [ ] Click "Predict Impact" on any policy
   - [ ] Results appear within 5 seconds

---

## 🔧 ADVANCED TROUBLESHOOTING

### **Enable Debug Mode:**

1. **Backend Debug:**
```python
# In BECW/simple_main.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Frontend Debug:**
```javascript
// In browser console:
localStorage.setItem('debug', 'true');
// Reload page to see detailed logs
```

### **Check Network Traffic:**
1. Press F12 → Network tab
2. Click "Predict Impact" button
3. Look for API calls to `/api/civic-decision-making/`
4. Check response status and data

### **Verify API Responses:**
```bash
# Test each endpoint manually:
curl -X POST http://localhost:8000/api/civic-decision-making/predict-policy-impact \
  -H "Content-Type: application/json" \
  -d '{"policy": "drought_mitigation", "location": "Turkana County", "timeframe": "5_years"}'
```

---

## 📞 GETTING HELP

### **If Issues Persist:**

1. **Check Server Logs:**
   - Look at terminal running `python simple_main.py`
   - Note any error messages or stack traces

2. **Browser Console:**
   - Press F12 → Console
   - Copy any error messages

3. **Test Environment:**
   - Python version: `python --version`
   - Node version: `node --version`
   - Operating system

4. **Network Configuration:**
   - Firewall settings
   - Proxy configuration
   - Port availability

---

## 🎯 SUCCESS INDICATORS

### **System Working Correctly When:**

✅ **Backend:**
- Server starts without errors
- API documentation accessible at `/docs`
- Database queries return data
- All test endpoints respond

✅ **Frontend:**
- Page loads without console errors
- All tabs (Decisions, Policies, Resources, Consensus) work
- Buttons respond within 5 seconds
- Results display properly

✅ **Integration:**
- API calls succeed (check Network tab)
- Data flows from backend to frontend
- Real-time updates work
- Error handling graceful

---

## 🏆 COMPETITION READINESS

### **Final Verification:**

1. **Demo Scenario Test:**
   - Select "Drought Mitigation Program"
   - Click "Predict Impact"
   - Verify results show within 3 seconds
   - Check all metrics display correctly

2. **Performance Check:**
   - All API calls complete under 5 seconds
   - No browser console errors
   - Smooth user interactions
   - Professional appearance

3. **Backup Plan:**
   - Screenshots of working system
   - Video recording of functionality
   - Offline demo data prepared
   - Alternative demo scenarios ready

**Your system is now bulletproof and competition-ready!** 🚀