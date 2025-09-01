import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import re
from werkzeug.utils import secure_filename
import mimetypes

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# File upload configuration
UPLOAD_FOLDER = 'uploads/videos'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_video_token():
    """Generate a unique token for video sharing"""
    return secrets.token_urlsafe(32)

# ============ AUTHENTICATION ROUTES ============

@app.route('/api/auth/profile/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile with celebrity status"""
    try:
        profile_result = supabase.table('profiles').select('*').eq('id', user_id).execute()
        
        if not profile_result.data:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile = profile_result.data[0]
        return jsonify({'profile': profile}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile/<user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """Update user profile"""
    try:
        data = request.get_json()
        
        # Remove sensitive fields that shouldn't be updated directly
        update_data = {k: v for k, v in data.items() if k not in ['id', 'email', 'created_at']}
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
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

# ============ CELEBRITY ROUTES ============

@app.route('/api/celebrities', methods=['GET'])
def get_celebrities():
    """Get all verified celebrities"""
    try:
        celebrities_result = supabase.table('profiles').select('*').eq('is_celebrity', True).eq('celebrity_verified', True).execute()
        return jsonify({'celebrities': celebrities_result.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/celebrities/<celebrity_id>/requests', methods=['GET'])
def get_celebrity_requests(celebrity_id):
    """Get all fan requests for a specific celebrity"""
    try:
        requests_result = supabase.table('video_requests').select('''
            *,
            requester:profiles!video_requests_requester_id_fkey(first_name, last_name, email)
        ''').eq('celebrity_id', celebrity_id).order('created_at', desc=True).execute()
        
        return jsonify({'requests': requests_result.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/celebrities/<celebrity_id>/verify', methods=['POST'])
def verify_celebrity(celebrity_id):
    """Admin route to verify celebrity status"""
    try:
        # In a real app, this would require admin authentication
        result = supabase.table('profiles').update({
            'celebrity_verified': True,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', celebrity_id).execute()
        
        if result.data:
            return jsonify({'message': 'Celebrity verified successfully'}), 200
        else:
            return jsonify({'error': 'Celebrity not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ VIDEO REQUEST ROUTES ============

@app.route('/api/requests', methods=['POST'])
def create_video_request():
    """Create a new video request from fan to celebrity"""
    try:
        data = request.get_json()
        
        required_fields = ['celebrity_id', 'requester_id', 'recipient_name', 'occasion', 'message_details']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        request_data = {
            'id': str(uuid.uuid4()),
            'celebrity_id': data['celebrity_id'],
            'requester_id': data['requester_id'],
            'recipient_name': data['recipient_name'],
            'occasion': data['occasion'],
            'message_details': data['message_details'],
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('video_requests').insert(request_data).execute()
        
        if result.data:
            return jsonify({
                'message': 'Video request created successfully',
                'request': result.data[0]
            }), 201
        else:
            return jsonify({'error': 'Failed to create request'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/requests/<request_id>/accept', methods=['POST'])
def accept_video_request(request_id):
    """Celebrity accepts a video request"""
    try:
        result = supabase.table('video_requests').update({
            'status': 'accepted',
            'accepted_at': datetime.utcnow().isoformat()
        }).eq('id', request_id).execute()
        
        if result.data:
            return jsonify({
                'message': 'Request accepted successfully',
                'request': result.data[0]
            }), 200
        else:
            return jsonify({'error': 'Request not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/requests/<request_id>/reject', methods=['POST'])
def reject_video_request(request_id):
    """Celebrity rejects a video request"""
    try:
        data = request.get_json()
        rejection_reason = data.get('reason', 'No reason provided')
        
        result = supabase.table('video_requests').update({
            'status': 'rejected',
            'rejection_reason': rejection_reason,
            'rejected_at': datetime.utcnow().isoformat()
        }).eq('id', request_id).execute()
        
        if result.data:
            return jsonify({
                'message': 'Request rejected',
                'request': result.data[0]
            }), 200
        else:
            return jsonify({'error': 'Request not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ VIDEO UPLOAD AND MANAGEMENT ============

@app.route('/api/videos/upload', methods=['POST'])
def upload_video():
    """Upload video file for celebrity response or family message"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: mp4, mov, avi, mkv, webm'}), 400
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Get additional data from form
        video_type = request.form.get('type', 'family')  # 'celebrity' or 'family'
        request_id = request.form.get('request_id')
        uploader_id = request.form.get('uploader_id')
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        
        # Generate shareable token for family videos
        share_token = generate_video_token() if video_type == 'family' else None
        
        # Create video record in database
        video_data = {
            'id': str(uuid.uuid4()),
            'filename': unique_filename,
            'original_filename': secure_filename(file.filename),
            'file_path': file_path,
            'uploader_id': uploader_id,
            'video_type': video_type,
            'title': title,
            'description': description,
            'share_token': share_token,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if request_id:
            video_data['request_id'] = request_id
        
        result = supabase.table('videos').insert(video_data).execute()
        
        if result.data:
            # If this is a celebrity response, update the request status
            if video_type == 'celebrity' and request_id:
                supabase.table('video_requests').update({
                    'status': 'completed',
                    'video_id': result.data[0]['id'],
                    'completed_at': datetime.utcnow().isoformat()
                }).eq('id', request_id).execute()
            
            response_data = {
                'message': 'Video uploaded successfully',
                'video': result.data[0]
            }
            
            # Include shareable link for family videos
            if share_token:
                response_data['share_url'] = f"{request.host_url}watch/{share_token}"
            
            return jsonify(response_data), 201
        else:
            # Clean up file if database insert failed
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': 'Failed to save video record'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/watch/<share_token>')
def get_video_by_token(share_token):
    """Get video information by share token"""
    try:
        video_result = supabase.table('videos').select('''
            *,
            uploader:profiles!videos_uploader_id_fkey(first_name, last_name)
        ''').eq('share_token', share_token).execute()
        
        if not video_result.data:
            return jsonify({'error': 'Video not found or expired'}), 404
        
        video = video_result.data[0]
        
        # Check if video exists on filesystem
        if not os.path.exists(video['file_path']):
            return jsonify({'error': 'Video file not found'}), 404
        
        return jsonify({'video': video}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/stream/<share_token>')
def stream_video(share_token):
    """Stream video file by share token"""
    try:
        video_result = supabase.table('videos').select('file_path, original_filename').eq('share_token', share_token).execute()
        
        if not video_result.data:
            return jsonify({'error': 'Video not found'}), 404
        
        video = video_result.data[0]
        file_path = video['file_path']
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        # Increment view count
        supabase.table('videos').update({
            'view_count': supabase.table('videos').select('view_count').eq('share_token', share_token).execute().data[0].get('view_count', 0) + 1,
            'last_viewed_at': datetime.utcnow().isoformat()
        }).eq('share_token', share_token).execute()
        
        mimetype = mimetypes.guess_type(file_path)[0] or 'video/mp4'
        return send_file(file_path, mimetype=mimetype, as_attachment=False)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ FAMILY VIDEO ROUTES ============

@app.route('/api/family/videos', methods=['POST'])
def create_family_video():
    """Create a family video entry and return shareable link"""
    try:
        data = request.get_json()
        
        required_fields = ['sender_id', 'title']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        share_token = generate_video_token()
        
        video_data = {
            'id': str(uuid.uuid4()),
            'sender_id': data['sender_id'],
            'title': data['title'],
            'description': data.get('description', ''),
            'video_type': 'family',
            'share_token': share_token,
            'status': 'pending_upload',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('videos').insert(video_data).execute()
        
        if result.data:
            share_url = f"{request.host_url}watch/{share_token}"
            return jsonify({
                'message': 'Family video created successfully',
                'video': result.data[0],
                'share_url': share_url
            }), 201
        else:
            return jsonify({'error': 'Failed to create video'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/family/videos/<video_id>/upload', methods=['POST'])
def upload_family_video_file(video_id):
    """Upload the actual video file for a family video"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Update video record
        result = supabase.table('videos').update({
            'filename': unique_filename,
            'original_filename': secure_filename(file.filename),
            'file_path': file_path,
            'status': 'completed',
            'uploaded_at': datetime.utcnow().isoformat()
        }).eq('id', video_id).execute()
        
        if result.data:
            return jsonify({
                'message': 'Video uploaded successfully',
                'video': result.data[0]
            }), 200
        else:
            # Clean up file if database update failed
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': 'Failed to update video record'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ ADMIN ROUTES ============

@app.route('/api/admin/celebrities/pending', methods=['GET'])
def get_pending_celebrities():
    """Get celebrities pending verification"""
    try:
        pending_result = supabase.table('profiles').select('*').eq('is_celebrity', True).eq('celebrity_verified', False).execute()
        return jsonify({'pending_celebrities': pending_result.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/celebrities/<celebrity_id>/verify', methods=['POST'])
def admin_verify_celebrity(celebrity_id):
    """Admin verify celebrity"""
    try:
        data = request.get_json()
        
        update_data = {
            'celebrity_verified': True,
            'verification_date': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if data.get('category'):
            update_data['celebrity_category'] = data['category']
        if data.get('bio'):
            update_data['celebrity_bio'] = data['bio']
        if data.get('price'):
            update_data['celebrity_price'] = data['price']
        
        result = supabase.table('profiles').update(update_data).eq('id', celebrity_id).execute()
        
        if result.data:
            return jsonify({
                'message': 'Celebrity verified successfully',
                'celebrity': result.data[0]
            }), 200
        else:
            return jsonify({'error': 'Celebrity not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ VIDEO VIEWER ROUTES ============

@app.route('/api/videos/public/<share_token>')
def view_shared_video(share_token):
    """Public route for viewing shared videos"""
    try:
        video_result = supabase.table('videos').select('''
            *,
            sender:profiles!videos_sender_id_fkey(first_name, last_name),
            uploader:profiles!videos_uploader_id_fkey(first_name, last_name)
        ''').eq('share_token', share_token).execute()
        
        if not video_result.data:
            return jsonify({'error': 'Video not found'}), 404
        
        video = video_result.data[0]
        
        # Don't expose sensitive file paths in public API
        public_video_data = {
            'id': video['id'],
            'title': video['title'],
            'description': video['description'],
            'video_type': video['video_type'],
            'created_at': video['created_at'],
            'sender': video.get('sender'),
            'uploader': video.get('uploader')
        }
        
        return jsonify({'video': public_video_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ UTILITY ROUTES ============

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_platform_stats():
    """Get platform statistics"""
    try:
        # Get counts
        celebrities_count = supabase.table('profiles').select('id', count='exact').eq('celebrity_verified', True).execute()
        users_count = supabase.table('profiles').select('id', count='exact').execute()
        videos_count = supabase.table('videos').select('id', count='exact').execute()
        requests_count = supabase.table('video_requests').select('id', count='exact').execute()
        
        return jsonify({
            'stats': {
                'verified_celebrities': celebrities_count.count if celebrities_count.count else 0,
                'total_users': users_count.count if users_count.count else 0,
                'total_videos': videos_count.count if videos_count.count else 0,
                'total_requests': requests_count.count if requests_count.count else 0
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 100MB'}), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)