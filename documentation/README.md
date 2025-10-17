# Climate Witness Chain - Backend

A comprehensive backend API for the Climate Witness Chain platform, featuring OTP authentication, M-Pesa payments, blockchain integration, and MeTTa-powered AI verification.

## 🚀 Features

- **OTP Authentication**: Secure 2FA with SMS verification
- **M-Pesa Integration**: Seamless mobile payments via Daraja API
- **Blockchain Integration**: Polygon network for transparent transactions
- **MeTTa AI**: Advanced climate data verification using MeTTa reasoning
- **Admin Dashboard**: Comprehensive analytics and user management
- **Real-time Notifications**: Event-driven updates and alerts

## 📋 Prerequisites

- Python 3.8+
- SQLite (included) or PostgreSQL for production
- M-Pesa Developer Account (optional for demo mode)
- Twilio Account (optional for SMS)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BECW
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -c "import asyncio; from app.database.migrations import reset_database; asyncio.run(reset_database())"
   ```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

#### Required Settings
```bash
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./climate_witness.db
```

#### M-Pesa Configuration (Optional)
```bash
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_BUSINESS_SHORT_CODE=174379
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://your-domain.com/api/payments/mpesa/callback
MPESA_ENVIRONMENT=sandbox  # or production
```

#### SMS Configuration (Optional)
```bash
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

#### Blockchain Configuration (Optional)
```bash
POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com/
PRIVATE_KEY=your_private_key
```

## 🚀 Running the Application

### Development Mode
```bash
python start_server.py
```

### Production Mode
```bash
python start_production.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - Standard login
- `POST /api/auth/login-with-otp` - Login with OTP verification
- `POST /api/auth/verify-otp` - Verify OTP code
- `POST /api/auth/resend-otp` - Resend OTP
- `GET /api/auth/me` - Get current user

### Payments
- `POST /api/payments/mpesa/stk-push` - Initiate M-Pesa payment
- `GET /api/payments/transaction/{id}` - Get transaction status
- `GET /api/payments/transactions` - Get user transactions
- `GET /api/payments/test` - Test payment service

### Events
- `POST /api/events` - Submit climate event
- `GET /api/events` - List events
- `GET /api/events/{id}` - Get event details
- `PUT /api/events/{id}/verify` - Verify event

### Admin
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `GET /api/admin/users` - User management
- `GET /api/admin/events` - Event management

## 🧪 Testing

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# Test payment service
curl http://localhost:8000/api/payments/test

# Test OTP login
curl -X POST http://localhost:8000/api/auth/login-with-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password", "phone_number": "0712345678"}'
```

### Sample Users
- **Admin**: admin@climatewitness.com (password: admin123)
- **User**: amina@example.com (password: demo123)

## 🔧 Development

### Project Structure
```
BECW/
├── app/
│   ├── api/routes/          # API endpoints
│   ├── services/            # Business logic
│   ├── database/            # Database models and migrations
│   └── utils/               # Utility functions
├── metta/                   # MeTTa knowledge files
├── uploads/                 # File uploads
├── logs/                    # Application logs
└── main.py                  # FastAPI application
```

### Adding New Features
1. Create service in `app/services/`
2. Add routes in `app/api/routes/`
3. Update database schema in `app/database/migrations.py`
4. Add tests and documentation

## 🐳 Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "start_production.py"]
```

## 🔒 Security

- Environment variables for sensitive data
- JWT token authentication
- Rate limiting on API endpoints
- Input validation and sanitization
- CORS configuration
- SQL injection prevention

## 📊 Monitoring

- Health check endpoint: `/health`
- Application logs in `logs/` directory
- Database query logging
- Error tracking and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the logs in `logs/app.log`
- Ensure all environment variables are configured
- Verify database connectivity

## 🔄 Updates

### Version 1.0.0
- Initial release with OTP authentication
- M-Pesa payment integration
- Admin dashboard
- MeTTa AI verification
- Blockchain integration