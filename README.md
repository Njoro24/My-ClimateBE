# Climate Witness Chain - Backend API

A production-ready FastAPI backend for community-driven climate data collection using MeTTa knowledge atoms.

## Quick Start

### Option 1: Direct Start
```bash
python main.py
```

### Option 2: Using Start Script
```bash
python start.py
```

## Features

- **Authentication System**: JWT-based authentication with refresh tokens
- **Climate Data Collection**: Community-driven climate event reporting
- **MeTTa Integration**: Knowledge atom processing for climate data
- **Blockchain Integration**: Polygon/Mumbai testnet support
- **Payment Processing**: M-Pesa integration for micropayments
- **AI Analysis**: Explainable AI for climate pattern analysis
- **Community Verification**: Peer-to-peer event verification
- **Dashboard Analytics**: Real-time climate data visualization

## API Endpoints

The API runs on `http://localhost:8000` by default and includes:

- `/api/auth/*` - Authentication endpoints
- `/api/events/*` - Climate event management
- `/api/metta/*` - MeTTa knowledge processing
- `/api/climate/*` - Climate data analysis
- `/api/payments/*` - Payment processing
- `/api/explainable-ai/*` - AI analysis endpoints
- `/api/civic-decisions/*` - Civic decision making
- `/docs` - Interactive API documentation

## Environment Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Initialize database:
```bash
python init_dashboard_data.py
```

## Production Deployment

The application is configured for production deployment with:
- CORS enabled for frontend integration
- Database connection pooling
- Error handling and logging
- Health check endpoints

## Testing

Run feature tests:
```bash
python test_real_features.py
```

## Architecture

- **FastAPI**: Modern Python web framework
- **SQLite**: Lightweight database for development
- **MeTTa**: Knowledge atom processing
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production

## Support

For issues or questions, check the API documentation at `/docs` when the server is running.