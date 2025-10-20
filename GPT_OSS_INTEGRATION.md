# GPT-OSS-20B Integration for Climate Witness Chain

## Overview

This document describes the integration of OpenAI's GPT-OSS-20B model into the Climate Witness Chain platform. GPT-OSS-20B is a 20.9B parameter MoE (Mixture of Experts) transformer with advanced reasoning capabilities, perfect for enhancing our MeTTa knowledge processing and explainable AI features.

## Key Features

### 🧠 Enhanced MeTTa Reasoning
- **Symbolic Processing**: Advanced interpretation of MeTTa atoms and expressions
- **Pattern Recognition**: Identifies complex relationships in climate data
- **Chain-of-Thought**: Full reasoning transparency for debugging
- **Confidence Scoring**: Quantified uncertainty in reasoning results

### 🔍 Explainable AI Decisions
- **Comprehensive Explanations**: Multi-level explanations from citizen-friendly to technical
- **Decision Transparency**: Full reasoning chain for every AI decision
- **Bias Detection**: Identifies and explains potential algorithmic biases
- **Context Awareness**: Personalized explanations based on user profile

### ⛓️ Blockchain Integration
- **Smart Contract Analysis**: Security and optimization recommendations
- **Gas Optimization**: Suggestions for reducing transaction costs
- **Risk Assessment**: Fraud detection and security scoring
- **Economic Impact**: Analysis of payout calculations and insurance logic

### 👥 Community Verification
- **Consensus Analysis**: Advanced evaluation of community decisions
- **Fairness Metrics**: Bias detection across demographics and geography
- **Trust Network**: Analysis of user relationships and credibility
- **Manipulation Detection**: Identifies potential gaming of the system

### 🌍 Early Warning System
- **Predictive Analysis**: Climate event prediction with uncertainty quantification
- **Risk Assessment**: Multi-factor risk scoring for different event types
- **Timeline Prediction**: When and where events are likely to occur
- **Impact Analysis**: Economic and social impact projections

### 🏛️ DAO Governance
- **Proposal Analysis**: Comprehensive evaluation of governance proposals
- **Stakeholder Impact**: Analysis of how decisions affect different groups
- **Feasibility Assessment**: Technical and economic viability scoring
- **Alternative Solutions**: Suggestions for improved approaches

## API Endpoints

### Enhanced MeTTa Reasoning
```http
POST /api/gpt-oss/enhanced-metta-reasoning
Content-Type: application/json

{
  "query": "(verify-event drought_001 user_123)",
  "context": {
    "event_type": "drought",
    "location": "Kenya",
    "severity": "high"
  },
  "reasoning_level": "detailed"
}
```

### Explainable Verification
```http
POST /api/gpt-oss/explainable-verification
Content-Type: application/json

{
  "event_id": "evt_123456",
  "user_id": "usr_789012",
  "explanation_level": "comprehensive"
}
```

### Blockchain Analysis
```http
POST /api/gpt-oss/blockchain-analysis
Content-Type: application/json

{
  "contract_data": {
    "function": "processPayout",
    "parameters": {"eventId": "0x123", "amount": "0.01"},
    "gas_estimate": 150000
  },
  "analysis_type": "full"
}
```

### Community Verification Analysis
```http
POST /api/gpt-oss/community-verification-analysis
Content-Type: application/json

{
  "verification_data": {
    "event_id": "evt_123",
    "verifiers": ["user_1", "user_2", "user_3"],
    "votes": [true, true, false],
    "trust_scores": [85, 92, 67]
  },
  "bias_detection": true
}
```

### Early Warning Prediction
```http
POST /api/gpt-oss/early-warning-prediction
Content-Type: application/json

{
  "location_data": {
    "latitude": -1.2921,
    "longitude": 36.8219,
    "region": "Nairobi, Kenya"
  },
  "historical_events": [],
  "prediction_horizon": "7_days"
}
```

### DAO Governance Analysis
```http
POST /api/gpt-oss/dao-governance-analysis
Content-Type: application/json

{
  "proposal_data": {
    "title": "Increase verification rewards",
    "description": "Proposal to increase base rewards from 0.1 to 0.15 ETH",
    "impact_areas": ["economics", "participation"],
    "voting_power": {"for": 1250, "against": 340}
  },
  "analysis_depth": "comprehensive"
}
```

### Function Calling
```http
POST /api/gpt-oss/function-calling
Content-Type: application/json

{
  "function_name": "trigger_micro_insurance",
  "parameters": {
    "event_id": "evt_123",
    "user_id": "usr_456",
    "payout_amount": 0.05
  },
  "execution_mode": "safe"
}
```

## Configuration

### Environment Variables

```bash
# GPT-OSS Configuration
ASI_API_KEY=your-asi-api-key-here
GPT_OSS_ENABLED=true
GPT_OSS_BASE_URL=https://inference.asicloud.cudos.org/v1
GPT_OSS_MODEL=openai/gpt-oss-20b
```

### Service Initialization

```python
from app.services.gpt_oss_service import GPTOSSService

# Initialize service
gpt_service = GPTOSSService()

# Check status
status = await gpt_service.get_service_status()
print(f"GPT-OSS Connected: {status.get('api_connected', False)}")
```

## Integration with Existing Services

### MeTTa Service Integration
The GPT-OSS service works alongside the existing MeTTa service without replacing it:

```python
# Enhanced reasoning combines both services
metta_result = metta_kb.run_metta_function(query)
gpt_enhancement = await gpt_service.enhanced_metta_reasoning(query, context)

# Both results are available for comparison and validation
```

### Explainable AI Enhancement
The existing explainable AI routes now automatically use GPT-OSS when available:

```python
# Automatic fallback to standard explanations if GPT-OSS unavailable
if GPT_OSS_AVAILABLE:
    enhanced_explanation = await gpt_service.explainable_verification_decision(event_id, user_id)
else:
    standard_explanation = generate_standard_explanation(event_id, user_id)
```

## Frontend Integration

### Service Usage
```javascript
import gptOssService from '../services/gptOssService';

// Enhanced MeTTa reasoning
const result = await gptOssService.enhancedMeTTaReasoning(
  '(verify-event drought_001 user_123)',
  { event_type: 'drought', location: 'Kenya' }
);

// Explainable verification
const explanation = await gptOssService.getExplainableVerification(
  'evt_123456',
  'usr_789012'
);
```

### Status Checking
```javascript
// Check if GPT-OSS is available
const status = await gptOssService.getServiceStatus();
if (status.success && status.service_status?.api_connected) {
  // Use enhanced features
  setEnhancedMode(true);
} else {
  // Fall back to standard features
  setEnhancedMode(false);
}
```

## Model Specifications

### GPT-OSS-20B Details
- **Parameters**: 20.9B total, 3.6B active per token
- **Architecture**: Mixture of Experts (MoE) Transformer
- **Context Window**: 131,072 tokens (YaRN extended)
- **Quantization**: MXFP4 (~12.8 GiB checkpoint)
- **Memory Requirements**: ~16 GB for inference
- **License**: Apache 2.0

### Capabilities
- **Instruction Following**: Strong adherence to complex instructions
- **Tool Use**: Web search, Python execution, function calling
- **Structured Outputs**: JSON, XML, and custom format generation
- **Reasoning Effort**: Adjustable depth of analysis
- **Chain-of-Thought**: Full reasoning transparency

## Performance Considerations

### Cost Optimization
- **Input Tokens**: $0.03 per 1M tokens
- **Output Tokens**: $0.13 per 1M tokens
- **Caching**: Implement response caching for repeated queries
- **Batching**: Group similar requests when possible

### Response Times
- **Simple Queries**: 1-3 seconds
- **Complex Reasoning**: 5-15 seconds
- **Function Calling**: 3-8 seconds
- **Timeout**: 30 seconds maximum

### Error Handling
```python
try:
    result = await gpt_service.enhanced_metta_reasoning(query, context)
except Exception as e:
    # Graceful fallback to standard MeTTa processing
    logger.warning(f"GPT-OSS failed, using fallback: {e}")
    result = metta_kb.run_metta_function(query)
```

## Security Considerations

### API Key Management
- Store API keys in environment variables
- Use secure key rotation practices
- Monitor API usage and costs
- Implement rate limiting

### Data Privacy
- No sensitive user data sent to external APIs
- Anonymize personal information in queries
- Log only necessary information for debugging
- Comply with data protection regulations

### Input Validation
```python
def validate_query(query: str) -> bool:
    # Validate MeTTa syntax
    if not query.strip():
        return False
    
    # Check for malicious patterns
    dangerous_patterns = ['exec', 'eval', 'import', '__']
    if any(pattern in query.lower() for pattern in dangerous_patterns):
        return False
    
    return True
```

## Monitoring and Debugging

### Service Health Checks
```http
GET /api/gpt-oss/service-status
```

### Integration Testing
```http
POST /api/gpt-oss/test-integration
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Log GPT-OSS interactions
logger.info(f"GPT-OSS query: {query}")
logger.info(f"GPT-OSS response time: {response_time}s")
logger.info(f"GPT-OSS confidence: {confidence}")
```

### Metrics to Monitor
- API response times
- Success/failure rates
- Token usage and costs
- User satisfaction scores
- Explanation quality ratings

## Troubleshooting

### Common Issues

1. **API Key Invalid**
   ```
   Error: Authentication failed
   Solution: Check ASI_API_KEY environment variable
   ```

2. **Service Unavailable**
   ```
   Error: Connection timeout
   Solution: Check network connectivity and service status
   ```

3. **Rate Limiting**
   ```
   Error: Too many requests
   Solution: Implement exponential backoff and request queuing
   ```

4. **Memory Issues**
   ```
   Error: Out of memory
   Solution: Reduce context size or batch size
   ```

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger('app.services.gpt_oss_service').setLevel(logging.DEBUG)

# Test with simple query
result = await gpt_service.enhanced_metta_reasoning("(test-query)", {"debug": True})
```

## Future Enhancements

### Planned Features
- **Multi-language Support**: Explanations in local languages
- **Voice Interface**: Audio explanations for accessibility
- **Visual Reasoning**: Integration with image analysis
- **Federated Learning**: Collaborative model improvement
- **Real-time Streaming**: Live reasoning updates

### Research Directions
- **Custom Fine-tuning**: Domain-specific climate reasoning
- **Ensemble Methods**: Combining multiple AI models
- **Uncertainty Quantification**: Better confidence estimation
- **Causal Reasoning**: Understanding cause-effect relationships

## Contributing

### Adding New Capabilities
1. Extend `GPTOSSService` class with new methods
2. Add corresponding API routes
3. Update frontend service integration
4. Add comprehensive tests
5. Update documentation

### Testing
```bash
# Run GPT-OSS integration tests
python -m pytest tests/test_gpt_oss_integration.py

# Test frontend integration
npm test -- --testPathPattern=gptOssService
```

## Support

For issues related to GPT-OSS integration:
1. Check service status endpoint
2. Review logs for error messages
3. Verify API key and configuration
4. Test with simple queries first
5. Contact development team if issues persist

## License

This integration is part of the Climate Witness Chain project and follows the same licensing terms. GPT-OSS-20B model is licensed under Apache 2.0.