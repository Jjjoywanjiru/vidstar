import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import re
from werkzeug.utils import secure_filename
import mimetypes

load_dotenv()

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/assets')
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

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

# ============ AUTHENTICATION ROUTES ============

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    """Signup page"""
    return render_template('signup.html')

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Handle user registration"""
    try:
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        is_celebrity = request.form.get('is_celebrity') == 'on'
        
        # Validation
        if not email or not password or not first_name or not last_name:
            flash('All fields are required', 'error')
            return redirect(url_for('signup_page'))
        
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return redirect(url_for('signup_page'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('signup_page'))
        
        # Check if user already exists
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        if existing_user.data:
            flash('Email already registered', 'error')
            return redirect(url_for('signup_page'))
        
        # Hash password (in production, use proper password hashing)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user
        user_data = {
            'id': str(uuid.uuid4()),
            'email': email,
            'password_hash': password_hash,
            'first_name': first_name,
            'last_name': last_name,
            'is_celebrity': is_celebrity,
            'celebrity_verified': False,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            # Set session
            session['user_id'] = result.data[0]['id']
            session['is_celebrity'] = is_celebrity
            
            flash('Registration successful!', 'success')
            
            # Redirect based on user type
            if is_celebrity:
                return redirect(url_for('celebrity_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Registration failed. Please try again.', 'error')
            return redirect(url_for('signup_page'))
            
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('signup_page'))

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('login_page'))
        
        # Hash password to compare
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Find user
        user_result = supabase.table('users').select('*').eq('email', email).eq('password_hash', password_hash).execute()
        
        if user_result.data:
            user = user_result.data[0]
            session['user_id'] = user['id']
            session['is_celebrity'] = user['is_celebrity']
            
            flash('Login successful!', 'success')
            
            # Redirect based on user type
            if user['is_celebrity']:
                return redirect(url_for('celebrity_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login_page'))
            
    except Exception as e:
        flash(f'Login failed: {str(e)}', 'error')
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# ============ DASHBOARD ROUTES ============

@app.route('/dashboard')
def user_dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    if session.get('is_celebrity'):
        return redirect(url_for('celebrity_dashboard'))
    
    try:
        # Get user info
        user_result = supabase.table('users').select('*').eq('id', session['user_id']).execute()
        user = user_result.data[0] if user_result.data else None
        
        # Get verified celebrities
        celebrities_result = supabase.table('users').select('*').eq('is_celebrity', True).eq('celebrity_verified', True).execute()
        celebrities = celebrities_result.data
        
        # Get user's video requests
        requests_result = supabase.table('video_requests').select('''
            *,
            celebrity:users!video_requests_celebrity_id_fkey(first_name, last_name)
        ''').eq('requester_id', session['user_id']).order('created_at', desc=True).execute()
        requests = requests_result.data
        
        return render_template('user_dashboard.html', 
                             user=user, 
                             celebrities=celebrities, 
                             requests=requests)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/celebrity-dashboard')
def celebrity_dashboard():
    """Celebrity dashboard"""
    if 'user_id' not in session or not session.get('is_celebrity'):
        return redirect(url_for('login_page'))
    
    try:
        # Get celebrity info
        celebrity_result = supabase.table('users').select('*').eq('id', session['user_id']).execute()
        celebrity = celebrity_result.data[0] if celebrity_result.data else None
        
        # Get incoming requests
        requests_result = supabase.table('video_requests').select('''
            *,
            requester:users!video_requests_requester_id_fkey(first_name, last_name, email)
        ''').eq('celebrity_id', session['user_id']).order('created_at', desc=True).execute()
        requests = requests_result.data
        
        return render_template('celebrity_dashboard.html', 
                             celebrity=celebrity, 
                             requests=requests)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

# ============ VIDEO REQUEST ROUTES ============

@app.route('/api/requests/create', methods=['POST'])
def create_video_request():
    """Create a new video request from fan to celebrity"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    try:
        celebrity_id = request.form.get('celebrity_id')
        recipient_name = request.form.get('recipient_name')
        occasion = request.form.get('occasion')
        message_details = request.form.get('message_details')
        
        if not all([celebrity_id, recipient_name, occasion, message_details]):
            flash('All fields are required', 'error')
            return redirect(url_for('user_dashboard'))
        
        request_data = {
            'id': str(uuid.uuid4()),
            'celebrity_id': celebrity_id,
            'requester_id': session['user_id'],
            'recipient_name': recipient_name,
            'occasion': occasion,
            'message_details': message_details,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('video_requests').insert(request_data).execute()
        
        if result.data:
            flash('Video request sent successfully!', 'success')
        else:
            flash('Failed to send request. Please try again.', 'error')
            
        return redirect(url_for('user_dashboard'))
        
    except Exception as e:
        flash(f'Error creating request: {str(e)}', 'error')
        return redirect(url_for('user_dashboard'))

@app.route('/api/requests/<request_id>/accept', methods=['POST'])
def accept_video_request(request_id):
    """Celebrity accepts a video request"""
    if 'user_id' not in session or not session.get('is_celebrity'):
        return redirect(url_for('login_page'))
    
    try:
        result = supabase.table('video_requests').update({
            'status': 'accepted',
            'accepted_at': datetime.utcnow().isoformat()
        }).eq('id', request_id).eq('celebrity_id', session['user_id']).execute()
        
        if result.data:
            flash('Request accepted! You can now upload a video.', 'success')
        else:
            flash('Failed to accept request.', 'error')
            
        return redirect(url_for('celebrity_dashboard'))
        
    except Exception as e:
        flash(f'Error accepting request: {str(e)}', 'error')
        return redirect(url_for('celebrity_dashboard'))

@app.route('/api/requests/<request_id>/reject', methods=['POST'])
def reject_video_request(request_id):
    """Celebrity rejects a video request"""
    if 'user_id' not in session or not session.get('is_celebrity'):
        return redirect(url_for('login_page'))
    
    try:
        rejection_reason = request.form.get('reason', 'No reason provided')
        
        result = supabase.table('video_requests').update({
            'status': 'rejected',
            'rejection_reason': rejection_reason,
            'rejected_at': datetime.utcnow().isoformat()
        }).eq('id', request_id).eq('celebrity_id', session['user_id']).execute()
        
        if result.data:
            flash('Request rejected.', 'info')
        else:
            flash('Failed to reject request.', 'error')
            
        return redirect(url_for('celebrity_dashboard'))
        
    except Exception as e:
        flash(f'Error rejecting request: {str(e)}', 'error')
        return redirect(url_for('celebrity_dashboard'))

# ============ VIDEO UPLOAD ROUTES ============

@app.route('/upload/<request_id>')
def upload_page(request_id):
    """Video upload page for celebrities"""
    if 'user_id' not in session or not session.get('is_celebrity'):
        return redirect(url_for('login_page'))
    
    try:
        # Verify request belongs to this celebrity and is accepted
        request_result = supabase.table('video_requests').select('''
            *,
            requester:users!video_requests_requester_id_fkey(first_name, last_name)
        ''').eq('id', request_id).eq('celebrity_id', session['user_id']).eq('status', 'accepted').execute()
        
        if not request_result.data:
            flash('Invalid request or not authorized', 'error')
            return redirect(url_for('celebrity_dashboard'))
        
        video_request = request_result.data[0]
        return render_template('upload_video.html', request=video_request)
        
    except Exception as e:
        flash(f'Error loading upload page: {str(e)}', 'error')
        return redirect(url_for('celebrity_dashboard'))

@app.route('/api/videos/upload', methods=['POST'])
def upload_video():
    """Handle video upload"""
    if 'user_id' not in session or not session.get('is_celebrity'):
        return redirect(url_for('login_page'))
    
    try:
        if 'video' not in request.files:
            flash('No video file provided', 'error')
            return redirect(request.referrer)
        
        file = request.files['video']
        request_id = request.form.get('request_id')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.referrer)
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Allowed: mp4, mov, avi, mkv, webm', 'error')
            return redirect(request.referrer)
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Create video record
        video_data = {
            'id': str(uuid.uuid4()),
            'request_id': request_id,
            'celebrity_id': session['user_id'],
            'filename': unique_filename,
            'original_filename': secure_filename(file.filename),
            'file_path': file_path,
            'created_at': datetime.utcnow().isoformat()
        }
        
        video_result = supabase.table('videos').insert(video_data).execute()
        
        if video_result.data:
            # Update request status to completed
            supabase.table('video_requests').update({
                'status': 'completed',
                'video_id': video_result.data[0]['id'],
                'completed_at': datetime.utcnow().isoformat()
            }).eq('id', request_id).execute()
            
            flash('Video uploaded successfully!', 'success')
        else:
            # Clean up file if database insert failed
            if os.path.exists(file_path):
                os.remove(file_path)
            flash('Failed to save video record', 'error')
        
        return redirect(url_for('celebrity_dashboard'))
        
    except Exception as e:
        flash(f'Error uploading video: {str(e)}', 'error')
        return redirect(request.referrer)

# ============ VIDEO VIEWING ROUTES ============

@app.route('/watch/<video_id>')
def watch_video(video_id):
    """Watch uploaded video"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    try:
        # Get video info with request details
        video_result = supabase.table('videos').select('''
            *,
            request:video_requests!videos_request_id_fkey(
                recipient_name, 
                occasion, 
                message_details,
                requester_id
            ),
            celebrity:users!videos_celebrity_id_fkey(first_name, last_name)
        ''').eq('id', video_id).execute()
        
        if not video_result.data:
            flash('Video not found', 'error')
            return redirect(url_for('user_dashboard'))
        
        video = video_result.data[0]
        
        # Check if user has permission to view this video
        if not session.get('is_celebrity'):
            # Regular user can only view videos from their requests
            if video['request']['requester_id'] != session['user_id']:
                flash('Not authorized to view this video', 'error')
                return redirect(url_for('user_dashboard'))
        else:
            # Celebrity can only view their own uploaded videos
            if video['celebrity_id'] != session['user_id']:
                flash('Not authorized to view this video', 'error')
                return redirect(url_for('celebrity_dashboard'))
        
        return render_template('watch_video.html', video=video)
        
    except Exception as e:
        flash(f'Error loading video: {str(e)}', 'error')
        return redirect(url_for('user_dashboard'))

@app.route('/api/videos/stream/<video_id>')
def stream_video(video_id):
    """Stream video file"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    try:
        video_result = supabase.table('videos').select('file_path, request_id').eq('id', video_id).execute()
        
        if not video_result.data:
            return jsonify({'error': 'Video not found'}), 404
        
        video = video_result.data[0]
        
        # Verify user has permission to view this video
        request_result = supabase.table('video_requests').select('requester_id').eq('id', video['request_id']).execute()
        
        if request_result.data:
            if not session.get('is_celebrity') and request_result.data[0]['requester_id'] != session['user_id']:
                return jsonify({'error': 'Not authorized'}), 403
        
        file_path = video['file_path']
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        mimetype = mimetypes.guess_type(file_path)[0] or 'video/mp4'
        return send_file(file_path, mimetype=mimetype, as_attachment=False)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ ADMIN ROUTES ============

@app.route('/admin/verify-celebrity/<celebrity_id>')
def verify_celebrity(celebrity_id):
    """Admin route to verify celebrity (simplified for demo)"""
    try:
        result = supabase.table('users').update({
            'celebrity_verified': True,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', celebrity_id).execute()
        
        if result.data:
            flash('Celebrity verified successfully', 'success')
        else:
            flash('Celebrity not found', 'error')
            
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Error verifying celebrity: {str(e)}', 'error')
        return redirect(url_for('index'))

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)