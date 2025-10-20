# Climate Witness Dashboard - Real Data Integration

## Overview

The Climate Witness Dashboard now uses **real data** from the backend services, not demo data. All dashboard components connect to actual MeTTa-powered services that manage climate events, DAO governance, alerts, and community verification.

## Real Data Services

### 1. User Service (`app/services/user_service.py`)
- **Real functionality**: Creates users, manages trust scores, tracks verification history
- **MeTTa integration**: User atoms stored in knowledge base
- **Dashboard data**: User stats, trust scores, verification counts, location data



### 3. DAO Governance Service (`app/services/dao_governance_service.py`)
- **Real functionality**: Creates proposals, manages voting, executes funding
- **MeTTa integration**: Governance decisions and relief triggers
- **Dashboard data**: Active proposals, voting results, treasury balance

### 4. Alert Service (`app/services/alert_service.py`)
- **Real functionality**: Early warnings, real-time notifications, risk assessment
- **MeTTa integration**: AI-powered prediction alerts
- **Dashboard data**: Active alerts, severity levels, affected users

### 5. Community Verification Service (`app/services/community_verification_service.py`)
- **Real functionality**: Assigns verifiers, manages consensus, tracks accuracy
- **MeTTa integration**: Verifier selection and trust scoring
- **Dashboard data**: Verification assignments, accuracy rates, consensus status

## API Endpoints (Real Data)

All dashboard API calls connect to real backend endpoints:

```
/api/users/{userId}/stats          - Real user statistics

/api/dao-governance/proposals/active  - Real active proposals
/api/dao-governance/stats            - Real DAO statistics
/api/alerts/user/{userId}            - Real user alerts
/api/community-verification/assignments/{userId} - Real verification tasks
/api/community-verification/verifier-stats/{userId} - Real verifier metrics
```

## Dashboard Features (Production Ready)

### Real-Time Data
- **Live updates**: WebSocket connections for real-time alerts
- **Auto-refresh**: Dashboard data refreshes automatically
- **Status indicators**: Shows connection status and data freshness

### User Profile Integration
- **Trust scores**: Real trust scores from MeTTa calculations
- **Location data**: Actual user location for relevant alerts
- **Activity history**: Real event submissions and verifications



### DAO Governance
- **Proposal creation**: Submit real funding proposals
- **Voting system**: Cast votes on active proposals
- **Treasury tracking**: Monitor real DAO treasury balance

### Alert System
- **Early warnings**: AI-powered climate predictions
- **Location-based**: Alerts based on user's actual location
- **Severity levels**: Real risk assessment and escalation

### Community Verification
- **Assignment system**: Real verifier assignments based on trust scores
- **Consensus tracking**: Track verification consensus in real-time
- **Accuracy metrics**: Real verifier performance statistics

## Initialization Scripts

### Initialize Dashboard Data
```bash
cd BECW
python init_dashboard_data.py
```
This creates sample real data for testing:
- 5 users with different trust scores and locations
- 3 verified climate events

- DAO proposals for funding
- Climate alerts for different regions


### Test Dashboard Services
```bash
cd BECW
python test_dashboard_real_data.py
```
This tests all dashboard services to ensure they're working with real data.

## Frontend Integration

The frontend dashboard (`FECW/ClimateWitness/src/pages/Dashboard.jsx`) now includes:

### Real Data Display
- **User stats**: Shows actual trust scores, verification counts

- **DAO information**: Shows active proposals and voting status
- **Alert notifications**: Real-time climate alerts
- **Verification tasks**: Actual community verification assignments

### Interactive Features
- **Refresh buttons**: Manual data refresh for each section
- **Real-time indicators**: Shows live connection status
- **Error handling**: Graceful handling of API failures
- **Loading states**: Proper loading indicators during data fetch

### Navigation

- **DAO page**: Complete governance and voting interface
- **Alerts page**: Comprehensive alert management
- **Verification page**: Community verification dashboard

## MeTTa Integration

All services use MeTTa knowledge atoms for:
- **Decision making**: AI-powered governance and insurance decisions
- **Trust scoring**: Dynamic trust score calculations
- **Prediction**: Climate event predictions and early warnings
- **Consensus**: Community verification consensus mechanisms

## Production Deployment

The dashboard is production-ready with:
- **Real database**: SQLite database with actual data
- **Error handling**: Comprehensive error handling and fallbacks
- **Performance**: Optimized API calls and caching
- **Security**: Proper authentication and authorization
- **Scalability**: Designed to handle multiple users and events

## No Demo Data

⚠️ **Important**: This system uses **NO DEMO DATA**. All functionality is backed by real services, real database operations, and actual MeTTa AI processing. The dashboard reflects the true state of the Climate Witness DAO system.