import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from Flask!")

# Example: Get user profile data
@app.route('/api/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        profile_result = supabase.table('profiles').select('*').eq('id', user_id).execute()
        
        if not profile_result.data:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile = profile_result.data[0]
        return jsonify({'profile': profile}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Example: Update user profile
@app.route('/api/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    try:
        data = request.get_json()
        
        # Update profile data
        update_data = {}
        allowed_fields = ['first_name', 'last_name', 'username', 'phone', 
                         'date_of_birth', 'country', 'city', 'bio', 'avatar_url']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = supabase.table('profiles').update(update_data).eq('id', user_id).execute()
            
            if result.data:
                return jsonify({
                    'message': 'Profile updated successfully',
                    'profile': result.data[0]
                }), 200
            else:
                return jsonify({'error': 'Failed to update profile'}), 500
        else:
            return jsonify({'error': 'No valid fields to update'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Example: Get all user profiles (for admin purposes or user listing)
@app.route('/api/profiles', methods=['GET'])
def get_all_profiles():
    try:
        profiles_result = supabase.table('profiles').select('id, first_name, last_name, username, country, city, created_at').execute()
        return jsonify({'profiles': profiles_result.data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)