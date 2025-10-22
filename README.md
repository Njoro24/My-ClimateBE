# 🌍 Climate Witness Chain - Backend API

> **A community-driven platform for tracking climate events using AI-powered verification and transparent decision-making**

## 🎯 What This App Does

Climate Witness Chain helps communities around the world report and verify climate events like droughts, floods, and extreme weather. Think of it as a "Wikipedia for climate data" where:

- **Communities report** climate events with photos and GPS locations
- **AI verifies** submissions using satellite data and smart algorithms  
- **Everyone gets paid** for accurate reports through a fair insurance system
- **Decisions are transparent** - you can see exactly how the AI makes choices

## 🚀 Key Features

### 📸 **Climate Event Reporting**
- Upload photos of droughts, floods, storms, locust swarms
- Automatic GPS tagging and timestamp verification
- Real-time confidence scoring shows approval chances
- Community validation prevents fake reports

### 🤖 **Explainable AI System**
- **See how decisions are made** - no black box mystery
- **MeTTa reasoning engine** shows step-by-step logic
- **Multiple explanation levels**: Simple for citizens, technical for developers
- **Bias detection** ensures fair treatment across all regions

### 🛡️ **Media Integrity Protection**
- **Deepfake detection** prevents manipulated photos
- **Reverse image search** catches stock photos
- **Blockchain verification** creates tamper-proof records
- **EXIF analysis** validates photo authenticity

### 🏛️ **Democratic Decision Making**
- **Community voting** on important platform decisions
- **Quadratic voting** prevents wealthy users from dominating
- **Transparent governance** with public proposal discussions
- **Stakeholder participation** gives everyone a voice

### 💰 **Fair Insurance Payouts**
- **Trust-based scoring** rewards accurate reporters
- **Satellite correlation** confirms environmental conditions
- **Automatic payouts** for verified climate events
- **Economic impact analysis** helps communities plan

## 🧠 How We Use Explainable AI

### **Real-Time Confidence Meter**
```
Current Verification Confidence: 85% ✅

✅ GPS Location Verified (+20%)
✅ Photo Metadata Authentic (+18%) 
✅ Satellite Data Correlation (+25%)
⚠️ Waiting for Community Reports (+12%)
✅ Damage Description Complete (+10%)
```

**Why This Matters:** Users know their approval chances before submitting, reducing fraud and improving quality.

### **MeTTa Reasoning Engine**
```metta
; How the AI decides to verify a drought report
!(verify-climate-event drought user_001 evidence_bundle)
!(correlate-satellite-data location timestamp)
!(analyze-community-consensus nearby_reports)
!(calculate-confidence-score all_factors)
; Result: 92% confidence - APPROVED
```

**Why This Matters:** Every AI decision can be traced, audited, and understood by humans.

### **GPT-OSS-20B Enhanced Analysis**
We integrate GPT-OSS-20B (open-source 20 billion parameter model) for:
- **Natural language processing** of climate event descriptions
- **Enhanced reasoning** that combines with MeTTa symbolic logic
- **Contextual understanding** of complex climate scenarios
- **Multi-language support** for global communities
- **Advanced pattern recognition** in climate data

**Neural-Symbolic AI:** GPT-OSS-20B handles natural language while MeTTa provides logical reasoning, creating a powerful hybrid system.

### **Bias Detection & Fairness**
- **Geographic bias**: Ensures all regions get fair treatment
- **Demographic bias**: Prevents discrimination based on user characteristics  
- **Temporal bias**: Catches suspicious timing patterns
- **Algorithmic bias**: Monitors AI fairness across different groups

## 🛡️ How We Use Media Integrity

### **Photo Verification Pipeline**
1. **EXIF Analysis** - Checks camera metadata for authenticity
2. **Deepfake Detection** - Uses AI to spot manipulated images
3. **Reverse Image Search** - Prevents use of stock photos
4. **Blockchain Hashing** - Creates tamper-proof image records
5. **Consistency Analysis** - Compares multiple photos for coherence

### **Misinformation Prevention**
- **Source credibility scoring** based on historical accuracy
- **Cross-reference validation** with multiple data sources
- **Pattern matching** against known misinformation campaigns
- **Community fact-checking** with reputation-based weighting

### **Content Authenticity**
- **Immutable audit trails** track every edit and decision
- **Cryptographic signatures** prove content hasn't been altered
- **Transparent provenance** shows the complete history of each report
- **Decentralized verification** prevents single points of failure

## 🛠️ Technical Stack

- **FastAPI** - Modern Python web framework
- **MeTTa** - Symbolic reasoning and knowledge representation
- **GPT-OSS-20B** - Open-source large language model for enhanced AI analysis
- **PostgreSQL** - Reliable data storage
- **Blockchain** - Immutable record keeping
- **Satellite APIs** - Real-time environmental data
- **AI/ML Models** - Image analysis and fraud detection

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run the Server
```bash
python main.py
```

### 4. View API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation

## 📚 API Endpoints

### **Core Features**
- `POST /api/events/` - Submit climate event
- `GET /api/events/` - List all events
- `POST /api/auth/login` - User authentication
- `GET /api/users/profile` - User profile

### **AI & Verification**
- `POST /api/explainable-ai/explain-decision` - Get AI reasoning
- `POST /api/real-time-verification/calculate-confidence` - Live confidence scoring
- `GET /api/explainable-ai/fairness-metrics` - Bias analysis
- `POST /api/media-integrity/verify-content` - Content verification
- `POST /api/gpt-oss/analyze` - GPT-OSS-20B enhanced analysis
- `POST /api/gpt-oss/neural-symbolic` - Hybrid AI reasoning

### **Community & Governance**
- `POST /api/civic-decisions/create-proposal` - Create governance proposal
- `POST /api/community-verification/validate` - Community validation
- `GET /api/dao-governance/proposals` - List proposals
- `POST /api/alerts/create` - Create early warning

## 🔧 Configuration

### **Environment Variables**
```bash
DATABASE_URL=postgresql://user:pass@localhost/climatedb
BLOCKCHAIN_RPC_URL=https://your-blockchain-node
SATELLITE_API_KEY=your-satellite-api-key
GPT_OSS_API_URL=http://localhost:8080  # GPT-OSS-20B model endpoint
GPT_OSS_API_KEY=your-gpt-oss-key      # Optional authentication
OPENAI_API_KEY=your-openai-key         # Fallback for enhanced AI
```

### **AI Integration Architecture**

**MeTTa Knowledge Base** - Symbolic reasoning files in `/metta/` directory:
- `explainable_ai_enhanced.metta` - AI reasoning logic
- `real_time_verification.metta` - Confidence calculation
- `media_integrity_enhanced.metta` - Content verification
- `civic_decision_enhanced.metta` - Governance logic

**GPT-OSS-20B Integration** - Neural language processing:
- `/app/services/gpt_oss_service.py` - GPT-OSS API integration
- `/app/api/routes/gpt_oss_ai.py` - Enhanced AI endpoints
- Hybrid neural-symbolic reasoning combining both systems

## 🤝 For Developers

### **Adding New Features**
1. Create API route in `/app/api/routes/`
2. Add MeTTa reasoning in `/metta/`
3. Update main.py to include new router
4. Add tests in `/tests/`

### **Understanding MeTTa**
MeTTa is like SQL for logic - it lets us write rules that the AI follows:
```metta
; If user has high trust score AND satellite confirms event
; THEN approve with high confidence
(= (auto-approve $event $user)
   (and (> (trust-score $user) 80)
        (satellite-confirmed $event)))
```

### **Testing**
```bash
python -m pytest tests/
python test_real_features.py  # Test with real data
```

## 🌟 Why This Matters

Climate change affects everyone, but current systems for tracking and responding to climate events are:
- **Slow** - Takes weeks to verify reports
- **Opaque** - No one knows how decisions are made  
- **Unfair** - Wealthy regions get better treatment
- **Vulnerable** - Easy to manipulate with fake data

Climate Witness Chain fixes these problems with:
- **Speed** - Real-time verification and instant feedback
- **Transparency** - Every decision is explainable and auditable
- **Fairness** - AI bias detection ensures equal treatment
- **Security** - Blockchain and cryptography prevent manipulation

## 📞 Support

- **Documentation**: Visit `/docs` endpoint when server is running
- **Issues**: Check the GitHub issues page
- **Community**: Join our Discord for discussions
- **Email**: support@climatewitness.org

---

**Built  for communities fighting climate change**