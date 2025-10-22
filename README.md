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

### 🧠 **Interactive MeTTa Reasoning Engine** ⭐ NEW
- **Real-time civic decision making** with transparent AI reasoning
- **Interactive Q&A system** - ask the AI "why" and "what if" questions
- **Democratic participation** - propose alternative reasoning paths
- **Multi-stakeholder analysis** with bias detection and fairness metrics
- **Neural-symbolic integration** combining MeTTa logic with GPT-OSS-20B
- **Live reasoning visualization** showing AI decision process step-by-step

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

## 🧠 Interactive MeTTa Reasoning Engine ⭐ NEW

### **Real-Time Civic Decision Making**
Watch AI make civic decisions step-by-step with full transparency:

```
🏛️ Climate Adaptation Fund Allocation Decision

Step 1: Issue Analysis ✅ (85% confidence)
├─ Analyzing $5M fund allocation across drought-affected regions
├─ 4 stakeholder groups with different priorities identified
└─ 3 evidence sources with 92% average credibility

Step 2: Stakeholder Assessment ✅ (88% confidence)  
├─ Government: Immediate relief priority
├─ Farmers: Long-term agricultural support
├─ Researchers: Evidence-based allocation
└─ NGOs: Vulnerable population focus

Step 3: Evidence Evaluation ✅ (92% confidence)
├─ Satellite data: 70% vegetation stress in Turkana
├─ Community reports: 156 verified drought impacts  
└─ Economic analysis: $2.3M estimated damages

Step 4: Democratic Principles ✅ (87% confidence)
├─ Ensuring transparent decision process
├─ Fair stakeholder representation verified
└─ Accountability mechanisms in place

Step 5: Decision Synthesis ✅ (89% confidence)
└─ Recommendation: 40% immediate relief, 35% agricultural support, 
   15% infrastructure, 10% monitoring
```

### **Interactive Q&A System**
Ask the AI anything about its reasoning:

**User:** "Why prioritize immediate relief over long-term support?"

**AI:** "The decision balances urgent humanitarian needs (40%) against sustainable development (35%) based on satellite data showing 70% vegetation stress and 156 verified community reports of immediate distress. The allocation ensures both crisis response and resilience building."

**User:** "What if we allocated 60% to immediate relief instead?"

**AI:** "Increasing immediate relief to 60% would help more people now but reduce long-term resilience funding to 25%. This could lead to recurring crises. Alternative scenario shows 15% higher short-term satisfaction but 25% lower long-term preparedness."

### **Democratic Participation Features**
- **Propose Alternatives:** Users can suggest different reasoning approaches
- **Bias Detection:** Real-time analysis of decision fairness across demographics
- **Stakeholder Impact:** Visualize how decisions affect different groups
- **Consensus Building:** Facilitate transparent community agreement

### **Technical Implementation**
```metta
; Interactive civic reasoning with transparency
!(interactive-civic-reasoning 
  "Climate Fund Allocation"
  [{"name": "Government", "type": "government", "priority": "immediate_relief"}]
  [{"type": "satellite_data", "credibility": 0.95}]
  "How should we allocate funds fairly?")

; Real-time bias detection
!(detect-comprehensive-bias decision_history demographics outcomes)

; Alternative scenario generation  
!(generate-alternative-scenarios decision_proposal stakeholders)
```

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

### **Interactive Reasoning** ⭐ NEW
- `POST /api/interactive-reasoning/start-interactive-reasoning` - Start civic reasoning session
- `POST /api/interactive-reasoning/query-reasoning` - Ask questions about AI reasoning
- `POST /api/interactive-reasoning/propose-alternative` - Propose alternative approaches
- `GET /api/interactive-reasoning/bias-analysis/{session_id}` - Analyze reasoning bias
- `WebSocket /api/interactive-reasoning/ws/reasoning/{session_id}` - Real-time updates
- `GET /api/interactive-reasoning/health` - Service health check

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
- `interactive_civic_reasoning.metta` - Interactive reasoning for civic decisions ⭐ NEW

**GPT-OSS-20B Integration** - Neural language processing:
- `/app/services/gpt_oss_service.py` - GPT-OSS API integration
- `/app/api/routes/gpt_oss_ai.py` - Enhanced AI endpoints
- `/app/api/routes/interactive_reasoning.py` - Interactive civic reasoning ⭐ NEW
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
python test_production_interactive_reasoning.py  # Test Interactive Reasoning ⭐ NEW
python test_api_endpoints.py  # Test API connectivity
```

### **Interactive Reasoning Testing**
```bash
# Test MeTTa + GPT-OSS integration
python test_production_interactive_reasoning.py

# Test API endpoints
python test_api_endpoints.py

# Test with sample civic decision
curl -X POST http://localhost:8000/api/interactive-reasoning/start-interactive-reasoning \
  -H "Content-Type: application/json" \
  -d '{
    "issue": "Climate Fund Allocation",
    "stakeholders": [{"name": "Government", "type": "government"}],
    "evidence": [{"type": "satellite_data", "credibility": 0.95}],
    "user_query": "How should we allocate funds?",
    "user_type": "citizen"
  }'
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
- **Democracy** - Interactive reasoning enables community participation in AI decisions ⭐ NEW

## 📞 Support

- **Documentation**: Visit `/docs` endpoint when server is running
- **Issues**: Check the GitHub issues page
- **Community**: Join our Discord for discussions
- **Email**: support@climatewitness.org

---

**Built  for communities fighting climate change**