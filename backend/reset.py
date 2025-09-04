import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def reset_supabase_auth_settings():
    """Reset Supabase authentication settings to defaults"""
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # You need service role key for this
    
    if not SERVICE_KEY:
        print("❌ SUPABASE_SERVICE_KEY is required for admin operations")
        print("Get it from: Supabase Dashboard -> Settings -> API -> service_role key")
        return
    
    # Base URL for Supabase Auth API
    auth_url = f"{SUPABASE_URL}/auth/v1/admin"
    
    headers = {
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json',
        'apikey': SERVICE_KEY
    }
    
    # 1. Check current settings
    print("📋 Checking current auth settings...")
    try:
        response = requests.get(f"{auth_url}/settings", headers=headers)
        if response.status_code == 200:
            print("Current settings:", json.dumps(response.json(), indent=2))
        else:
            print(f"Failed to get settings: {response.status_code}")
    except Exception as e:
        print(f"Error getting settings: {e}")
    
    # 2. Reset email restrictions
    print("\n🔄 Resetting email restrictions...")
    email_settings = {
        "enable_confirmations": True,
        "enable_secure_email_change_enabled": True,
        "enable_signup": True,
        "allowed_email_domains": [],
        "allowed_email_domains_enabled": False,
        "external_anonymous_users_enabled": False,
        "external_email_enabled": True,
        "external_phone_enabled": False
    }
    
    try:
        response = requests.put(f"{auth_url}/settings", headers=headers, json=email_settings)
        if response.status_code == 200:
            print("✅ Email restrictions reset")
        else:
            print(f"❌ Failed to reset email restrictions: {response.status_code}")
    except Exception as e:
        print(f"Error resetting email restrictions: {e}")
    
    # 3. Reset password policy
    print("\n🔄 Resetting password policy...")
    password_policy = {
        "min_length": 6,
        "required_characters": []
    }
    
    try:
        response = requests.put(f"{auth_url}/settings/password-policy", headers=headers, json=password_policy)
        if response.status_code == 200:
            print("✅ Password policy reset")
        else:
            print(f"❌ Failed to reset password policy: {response.status_code}")
    except Exception as e:
        print(f"Error resetting password policy: {e}")
    
    # 4. Check and disable RLS on auth tables if needed
    print("\n🔄 Checking RLS policies...")
    # This would require SQL execution, which needs database access
    
    print("\n🎉 Reset completed. Try signing up again.")

def manual_fixes():
    """Manual steps you should take in Supabase dashboard"""
    print("\n" + "="*50)
    print("MANUAL STEPS TO CHECK IN SUPABASE DASHBOARD:")
    print("="*50)
    print("1. Go to Authentication -> Settings")
    print("2. Check 'Enable email sign up' is ON")
    print("3. Check 'Allowed email domains' is EMPTY")
    print("4. Check 'Enable confirm email' is ON")
    print("5. Check SMTP settings are configured (or disable email confirmation temporarily)")
    print("6. Go to Authentication -> Providers -> Email")
    print("7. Ensure 'Enable email provider' is ON")
    print("8. Check 'Password minimum length' is 6 or less")
    print("9. Disable any custom password requirements")
    print("10. Go to Database -> Tables -> auth.users")
    print("11. Check if RLS is enabled (turn it off temporarily for testing)")
    print("="*50)

if __name__ == "__main__":
    reset_supabase_auth_settings()
    manual_fixes()