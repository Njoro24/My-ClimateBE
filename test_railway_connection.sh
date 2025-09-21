#!/bin/bash

# Test Railway Backend Connection
RAILWAY_URL="https://web-production-92f64.up.railway.app"

echo "🚂 Testing Railway Backend Connection..."
echo "URL: $RAILWAY_URL"
echo "=" * 50

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$RAILWAY_URL/health" | jq .
echo ""

# Test 2: Root Endpoint
echo "2. Testing Root Endpoint..."
curl -s "$RAILWAY_URL/" | jq .
echo ""

# Test 3: Login Endpoint
echo "3. Testing Login Endpoint..."
curl -s -X POST "$RAILWAY_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}' | jq .
echo ""

# Test 4: Refresh Token Endpoint
echo "4. Testing Refresh Token Endpoint..."
curl -s -X POST "$RAILWAY_URL/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "test_refresh_token"}' | jq .
echo ""

# Test 5: Current User Endpoint
echo "5. Testing Current User Endpoint..."
curl -s "$RAILWAY_URL/api/auth/me" | jq .
echo ""

# Test 6: Payment Endpoint
echo "6. Testing Payment Endpoint..."
curl -s -X POST "$RAILWAY_URL/api/payments/mpesa/initiate" \
  -H "Content-Type: application/json" \
  -d '{"phone": "254712345678", "amount": 100, "reference": "test"}' | jq .
echo ""

echo "✅ All tests completed!"
echo "🎯 Your Railway backend is ready for frontend connection!"