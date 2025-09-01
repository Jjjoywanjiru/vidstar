import os
import hashlib
import secrets
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from Flask!")

@app.route('/api/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    """Get user profile by ID"""
    try:
        profile_result = supabase.table('profiles').select('*').eq('id', user_id).execute()
        
        if not profile_result.data:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile = profile_result.data[0]
        return jsonify({'profile': profile}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles', methods=['GET'])
def get_all_profiles():
    """Get all user profiles"""
    try:
        profiles_result = supabase.table('profiles').select('*').execute()
        return jsonify({'profiles': profiles_result.data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    """Update user profile"""
    try:
        data = request.get_json()
        
        # Remove id and email from update data (shouldn't be changed)
        update_data = {k: v for k, v in data.items() if k not in ['id', 'email']}
        
        result = supabase.table('profiles').update(update_data).eq('id', user_id).execute()
        
        if result.data:
            return jsonify({
                'message': 'Profile updated successfully',
                'profile': result.data[0]
            }), 200
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile/<user_id>', methods=['DELETE'])
def delete_profile(user_id):
    """Delete user profile"""
    try:
        result = supabase.table('profiles').delete().eq('id', user_id).execute()
        
        if result.data:
            return jsonify({'message': 'Profile deleted successfully'}), 200
        else:
            return jsonify({'error': 'Profile not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)