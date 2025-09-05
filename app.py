from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file, abort
from supabase import create_client, Client
import bcrypt
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from config import Config
import mimetypes

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads/videos'
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Supabase client
supabase: Client = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

# Helper functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def allowed_video_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def get_file_size(file_path):
    return os.path.getsize(file_path)

def get_user_by_email(email):
    try:
        response = supabase.table('users').select('*').eq('email', email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_user_by_id(user_id):
    try:
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_celebrity_requests(celebrity_id):
    try:
        response = supabase.table('video_requests').select('*, requester:users!video_requests_requester_id_fkey(first_name, last_name, email)').eq('celebrity_id', celebrity_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting requests: {e}")
        return []

def get_user_requests(user_id):
    try:
        response = supabase.table('video_requests').select('*, celebrity:users!video_requests_celebrity_id_fkey(first_name, last_name)').eq('requester_id', user_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting requests: {e}")
        return []

def get_all_celebrities():
    try:
        response = supabase.table('users').select('id, first_name, last_name, bio, price_per_video').eq('is_celebrity', True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting celebrities: {e}")
        return []

def get_video_by_request_id(request_id):
    try:
        response = supabase.table('videos').select('*').eq('request_id', request_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting video: {e}")
        return None

def get_request_by_id(request_id):
    try:
        response = supabase.table('video_requests').select('*, celebrity:users!video_requests_celebrity_id_fkey(first_name, last_name), requester:users!video_requests_requester_id_fkey(first_name, last_name, email)').eq('id', request_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting request: {e}")
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            is_celebrity = 'is_celebrity' in request.form
            
            # Check if user already exists
            existing_user = get_user_by_email(email)
            if existing_user:
                flash('Email already registered. Please login instead.', 'error')
                return redirect(url_for('signup'))
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Insert user - no verification needed for celebrities
            user_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password_hash': hashed_password,
                'is_celebrity': is_celebrity,
                'celebrity_verified': is_celebrity  # Auto-verify if they sign up as celebrity
            }
            
            response = supabase.table('users').insert(user_data).execute()
            
            if response.data:
                flash('Account created successfully! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error creating account. Please try again.', 'error')
                
        except Exception as e:
            print(f"Signup error: {e}")
            flash('Error creating account. Please try again.', 'error')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            
            user = get_user_by_email(email)
            if user and check_password(password, user['password_hash']):
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['first_name'] = user['first_name']
                session['is_celebrity'] = user['is_celebrity']
                
                if user['is_celebrity']:
                    return redirect(url_for('celebrity_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'error')
                
        except Exception as e:
            print(f"Login error: {e}")
            flash('Error logging in. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('is_celebrity'):
        return redirect(url_for('celebrity_dashboard'))
    
    user_requests = get_user_requests(session['user_id'])
    celebrities = get_all_celebrities()
    
    return render_template('user_dashboard.html', 
                         user=session, 
                         requests=user_requests, 
                         celebrities=celebrities)

@app.route('/celebrity-dashboard')
def celebrity_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if not session.get('is_celebrity'):
        return redirect(url_for('dashboard'))
    
    celebrity_requests = get_celebrity_requests(session['user_id'])
    celebrity = get_user_by_id(session['user_id'])
    
    return render_template('celebrity_dashboard.html', 
                         celebrity=celebrity, 
                         requests=celebrity_requests)

@app.route('/api/requests/create', methods=['POST'])
def create_request():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        celebrity_id = request.form['celebrity_id']
        recipient_name = request.form['recipient_name']
        occasion = request.form['occasion']
        message_details = request.form['message_details']
        
        request_data = {
            'requester_id': session['user_id'],
            'celebrity_id': celebrity_id,
            'recipient_name': recipient_name,
            'occasion': occasion,
            'message_details': message_details,
            'status': 'pending'
        }
        
        response = supabase.table('video_requests').insert(request_data).execute()
        
        if response.data:
            flash('Video request sent successfully!', 'success')
        else:
            flash('Error sending request. Please try again.', 'error')
            
    except Exception as e:
        print(f"Request creation error: {e}")
        flash('Error sending request. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/api/requests/<request_id>/accept', methods=['POST'])
def accept_request(request_id):
    if 'user_id' not in session or not session.get('is_celebrity'):
        return redirect(url_for('login'))
    
    try:
        update_data = {
            'status': 'accepted',
            'accepted_at': datetime.utcnow().isoformat()
        }
        
        response = supabase.table('video_requests').update(update_data).eq('id', request_id).eq('celebrity_id', session['user_id']).execute()
        
        if response.data:
            flash('Request accepted successfully!', 'success')
        else:
            flash('Error accepting request.', 'error')
            
    except Exception as e:
        print(f"Accept request error: {e}")
        flash('Error accepting request.', 'error')
    
    return redirect(url_for('celebrity_dashboard'))

@app.route('/api/requests/<request_id>/reject', methods=['POST'])
def reject_request(request_id):
    if 'user_id' not in session or not session.get('is_celebrity'):
        return redirect(url_for('login'))
    
    try:
        rejection_reason = request.form.get('reason', '')
        
        update_data = {
            'status': 'rejected',
            'rejection_reason': rejection_reason
        }
        
        response = supabase.table('video_requests').update(update_data).eq('id', request_id).eq('celebrity_id', session['user_id']).execute()
        
        if response.data:
            flash('Request rejected.', 'success')
        else:
            flash('Error rejecting request.', 'error')
            
    except Exception as e:
        print(f"Reject request error: {e}")
        flash('Error rejecting request.', 'error')
    
    return redirect(url_for('celebrity_dashboard'))

@app.route('/upload-video/<request_id>')
def upload_video_page(request_id):
    if 'user_id' not in session or not session.get('is_celebrity'):
        return redirect(url_for('login'))
    
    # Verify this request belongs to the current celebrity and is accepted
    video_request = get_request_by_id(request_id)
    if not video_request or video_request['celebrity_id'] != session['user_id'] or video_request['status'] != 'accepted':
        flash('Invalid request or you do not have permission to upload for this request.', 'error')
        return redirect(url_for('celebrity_dashboard'))
    
    return render_template('upload_video.html', request=video_request)

@app.route('/api/upload-video/<request_id>', methods=['POST'])
def upload_video(request_id):
    if 'user_id' not in session or not session.get('is_celebrity'):
        return redirect(url_for('login'))
    
    # Verify this request belongs to the current celebrity
    video_request = get_request_by_id(request_id)
    if not video_request or video_request['celebrity_id'] != session['user_id']:
        flash('Invalid request or you do not have permission.', 'error')
        return redirect(url_for('celebrity_dashboard'))
    
    try:
        if 'video' not in request.files:
            flash('No video file selected.', 'error')
            return redirect(url_for('upload_video_page', request_id=request_id))
        
        file = request.files['video']
        if file.filename == '':
            flash('No video file selected.', 'error')
            return redirect(url_for('upload_video_page', request_id=request_id))
        
        if file and allowed_video_file(file.filename):
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Save file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Get file info
            file_size = get_file_size(file_path)
            file_type = mimetypes.guess_type(file_path)[0] or 'video/mp4'
            
            # Save video record to database
            video_data = {
                'request_id': request_id,
                'celebrity_id': session['user_id'],
                'filename': unique_filename,
                'original_filename': original_filename,
                'file_size': file_size,
                'file_type': file_type,
                'storage_path': file_path
            }
            
            video_response = supabase.table('videos').insert(video_data).execute()
            
            if video_response.data:
                video_id = video_response.data[0]['id']
                
                # Update request status to completed and link to video
                update_data = {
                    'status': 'completed',
                    'completed_at': datetime.utcnow().isoformat(),
                    'video_id': video_id
                }
                
                supabase.table('video_requests').update(update_data).eq('id', request_id).execute()
                
                flash('Video uploaded successfully!', 'success')
                return redirect(url_for('celebrity_dashboard'))
            else:
                # Clean up file if database insert failed
                os.remove(file_path)
                flash('Error saving video information. Please try again.', 'error')
        else:
            flash('Invalid file type. Please upload a valid video file (mp4, avi, mov, mkv, wmv, flv, webm).', 'error')
            
    except Exception as e:
        print(f"Upload error: {e}")
        flash('Error uploading video. Please try again.', 'error')
    
    return redirect(url_for('upload_video_page', request_id=request_id))

@app.route('/watch/<int:request_id>')
def watch_video(request_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get the request and verify the user has access
    video_request = get_request_by_id(request_id)
    if not video_request:
        flash('Video request not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if user is the requester or the celebrity
    if video_request['requester_id'] != session['user_id'] and video_request['celebrity_id'] != session['user_id']:
        flash('You do not have permission to view this video.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get the video
    video = get_video_by_request_id(request_id)
    if not video or video_request['status'] != 'completed':
        flash('Video not available or not yet completed.', 'error')
        if session.get('is_celebrity'):
            return redirect(url_for('celebrity_dashboard'))
        else:
            return redirect(url_for('dashboard'))
    
    return render_template('watch_video.html', request=video_request, video=video)

@app.route('/api/download-video/<int:video_id>')
def download_video(video_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get video info
        response = supabase.table('videos').select('*, request:video_requests!videos_request_id_fkey(requester_id, celebrity_id)').eq('id', video_id).execute()
        
        if not response.data:
            abort(404)
        
        video = response.data[0]
        
        # Check if user has permission to download
        if (video['request']['requester_id'] != session['user_id'] and 
            video['request']['celebrity_id'] != session['user_id']):
            abort(403)
        
        # Check if file exists
        if not os.path.exists(video['storage_path']):
            abort(404)
        
        # Log download (optional)
        try:
            download_data = {
                'video_id': video_id,
                'user_id': session['user_id'],
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            }
            supabase.table('video_downloads').insert(download_data).execute()
        except:
            pass  # Don't fail download if logging fails
        
        # Send file
        return send_file(
            video['storage_path'],
            as_attachment=True,
            download_name=video['original_filename'],
            mimetype=video['file_type']
        )
        
    except Exception as e:
        print(f"Download error: {e}")
        abort(500)

@app.route('/api/stream-video/<int:video_id>')
def stream_video(video_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get video info
        response = supabase.table('videos').select('*, request:video_requests!videos_request_id_fkey(requester_id, celebrity_id)').eq('id', video_id).execute()
        
        if not response.data:
            abort(404)
        
        video = response.data[0]
        
        # Check if user has permission to view
        if (video['request']['requester_id'] != session['user_id'] and 
            video['request']['celebrity_id'] != session['user_id']):
            abort(403)
        
        # Check if file exists
        if not os.path.exists(video['storage_path']):
            abort(404)
        
        # Stream file for viewing
        return send_file(
            video['storage_path'],
            mimetype=video['file_type']
        )
        
    except Exception as e:
        print(f"Stream error: {e}")
        abort(500)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Add these error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)