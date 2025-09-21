#!/usr/bin/env python3
"""
Generate secure secret keys for Climate Witness Chain
"""

import secrets
import string
import hashlib
from datetime import datetime

def generate_secure_key(length=64):
    """Generate a cryptographically secure random key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_climate_witness_key():
    """Generate a Climate Witness Chain specific key"""
    # Base components
    timestamp = str(int(datetime.now().timestamp()))
    random_part = secrets.token_urlsafe(32)
    app_identifier = "ClimateWitnessChain2024"
    
    # Combine and hash
    combined = f"{app_identifier}_{timestamp}_{random_part}"
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    
    return f"CWC_{hashed[:48]}_PROD"

def main():
    print("🔐 Climate Witness Chain - Secret Key Generator")
    print("=" * 60)
    
    # Generate different types of keys
    keys = {
        "Simple Secure Key": generate_secure_key(64),
        "URL-Safe Key": secrets.token_urlsafe(48),
        "Hex Key": secrets.token_hex(32),
        "Climate Witness Key": generate_climate_witness_key()
    }
    
    print("\n🔑 Generated Secret Keys:")
    print("-" * 60)
    
    for key_type, key_value in keys.items():
        print(f"\n{key_type}:")
        print(f"{key_value}")
    
    print("\n" + "=" * 60)
    print("📋 RECOMMENDED FOR PRODUCTION:")
    print("=" * 60)
    
    recommended_key = generate_climate_witness_key()
    print(f"\nSECRET_KEY={recommended_key}")
    
    print("\n" + "=" * 60)
    print("🛡️ SECURITY NOTES:")
    print("=" * 60)
    print("1. ✅ Use the recommended key for production")
    print("2. ✅ Never commit secret keys to version control")
    print("3. ✅ Store in Render environment variables only")
    print("4. ✅ Regenerate keys if compromised")
    print("5. ✅ Use different keys for different environments")
    
    print("\n🚀 RENDER DEPLOYMENT:")
    print("=" * 60)
    print("Add this to Render Environment Variables:")
    print(f"SECRET_KEY={recommended_key}")
    
    return recommended_key

if __name__ == "__main__":
    main()