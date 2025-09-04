import os
import uuid
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

# Debug: Print environment variables (remove in production)
print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "SUPABASE_KEY: None")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client created successfully")
except Exception as e:
    print(f"Error creating Supabase client: {e}")
    supabase = None

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

@app.route('/email-verification')
def email_verification_page():
    """Email verification page"""
    return render_template('email_verification.html')

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Handle user registration with email verification"""
    try:
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        is_celebrity = request.form.get('is_celebrity') == 'on'
        
        # Debug logging
        print(f"Signup attempt for: {email}")
        print(f"Is celebrity: {is_celebrity}")
        
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
        
        try:
            # Test Supabase connection first
            print("Testing Supabase connection...")
            test_result = supabase.table('users').select('count').execute()
            print(f"Supabase connection successful: {test_result}")
            
            # Use Supabase Auth to create user
            print("Creating user with Supabase Auth...")
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "is_celebrity": is_celebrity
                    }
                }
            })
            
            print(f"Auth response: {auth_response}")
            
            if auth_response.user:
                print(f"User created with ID: {auth_response.user.id}")
                
                # Create profile in users table
                user_data = {
                    'id': auth_response.user.id,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_celebrity': is_celebrity,
                    'celebrity_verified': False,
                    'email_verified': False,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                print(f"Inserting user data: {user_data}")
                result = supabase.table('users').insert(user_data).execute()
                print(f"Insert result: {result}")
                
                if result.data:
                    flash('Registration successful! Please check your email to verify your account.', 'success')
                    return redirect(url_for('email_verification_page'))
                else:
                    print(f"Insert failed: {result}")
                    flash('Registration failed. Could not create user profile.', 'error')
                    return redirect(url_for('signup_page'))
            else:
                print("No user returned from auth.sign_up")
                flash('Registration failed. Please try again.', 'error')
                return redirect(url_for('signup_page'))
                
        except Exception as auth_error:
            print(f"Auth error: {str(auth_error)}")
            error_message = str(auth_error)
            if "already registered" in error_message.lower() or "already been registered" in error_message.lower():
                flash('This email is already registered. Please try logging in instead.', 'error')
            else:
                flash(f'Registration failed: {error_message}', 'error')
            return redirect(url_for('signup_page'))
            
    except Exception as e:
        print(f"General error in signup: {str(e)}")
        flash(f'An error occurred during registration: {str(e)}', 'error')
        return redirect(url_for('signup_page'))

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        # Debug: Print all form data
        print("Login form data:", dict(request.form))
        
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Login attempt: email={email}, password={'*' * len(password) if password else 'None'}")
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('login_page'))
        
        if not supabase:
            flash('Database connection error', 'error')
            return redirect(url_for('login_page'))
        
        try:
            print("Attempting Supabase login...")
            # Use Supabase Auth to sign in
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            print(f"Auth response: {auth_response}")
            print(f"User: {auth_response.user}")
            print(f"Session: {auth_response.session}")
            
            if auth_response.user:
                print(f"User logged in: {auth_response.user.id}")
                print(f"Email confirmed at: {auth_response.user.email_confirmed_at}")
                
                # Check if email is verified using Supabase Auth's property
                if not auth_response.user.email_confirmed_at:
                    flash('Please verify your email address before logging in. Check your inbox.', 'error')
                    return redirect(url_for('email_verification_page'))
                
                # Get user profile
                print("Fetching user profile...")
                user_result = supabase.table('users').select('*').eq('id', auth_response.user.id).execute()
                print(f"User profile result: {user_result}")
                
                if user_result.data:
                    user = user_result.data[0]
                    print(f"User profile: {user}")
                    
                    # Update email verification status if needed
                    if not user.get('email_verified', False):
                        print("Updating email verification status...")
                        supabase.table('users').update({
                            'email_verified': True,
                            'updated_at': datetime.utcnow().isoformat()
                        }).eq('id', user['id']).execute()
                    
                    # Set session
                    session['user_id'] = user['id']
                    session['email'] = user['email']
                    session['is_celebrity'] = user['is_celebrity']
                    session['access_token'] = auth_response.session.access_token
                    
                    print(f"Session set: user_id={session['user_id']}, is_celebrity={session['is_celebrity']}")
                    
                    flash('Login successful!', 'success')
                    
                    # Redirect based on user type
                    if user['is_celebrity']:
                        print("Redirecting to celebrity dashboard")
                        return redirect(url_for('celebrity_dashboard'))
                    else:
                        print("Redirecting to user dashboard")
                        return redirect(url_for('user_dashboard'))
                else:
                    print("User profile not found in database")
                    flash('User profile not found', 'error')
                    return redirect(url_for('login_page'))
            else:
                print("No user returned from auth")
                flash('Invalid email or password', 'error')
                return redirect(url_for('login_page'))
                
        except Exception as auth_error:
            print(f"Auth error during login: {auth_error}")
            error_message = str(auth_error)
            if "invalid" in error_message.lower():
                flash('Invalid email or password', 'error')
            elif "not confirmed" in error_message.lower():
                flash('Please verify your email address before logging in', 'error')
                return redirect(url_for('email_verification_page'))
            else:
                flash(f'Login failed: {error_message}', 'error')
            return redirect(url_for('login_page'))
            
    except Exception as e:
        print(f"General login error: {e}")
        flash(f'Login failed: {str(e)}', 'error')
        return redirect(url_for('login_page'))

@app.route('/api/auth/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification"""
    try:
        email = request.form.get('email')
        
        if not email:
            flash('Email is required', 'error')
            return redirect(url_for('email_verification_page'))
        
        if not supabase:
            flash('Database connection error', 'error')
            return redirect(url_for('email_verification_page'))
        
        # Resend verification email
        supabase.auth.resend({
            "type": "signup",
            "email": email
        })
        
        flash('Verification email sent! Please check your inbox.', 'success')
        return redirect(url_for('email_verification_page'))
        
    except Exception as e:
        print(f"Error sending verification email: {e}")
        flash(f'Error sending verification email: {str(e)}', 'error')
        return redirect(url_for('email_verification_page'))

@app.route('/logout')
def logout():
    """Handle user logout"""
    try:
        if 'access_token' in session and supabase:
            # Sign out from Supabase
            supabase.auth.sign_out()
    except Exception as e:
        print(f"Error during Supabase signout: {e}")
    
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# ============ DASHBOARD ROUTES ============

@app.route('/dashboard')
def user_dashboard():
    """User dashboard"""
    print(f"User dashboard accessed. Session: {dict(session)}")
    
    if 'user_id' not in session:
        print("No user_id in session, redirecting to login")
        return redirect(url_for('login_page'))
    
    if session.get('is_celebrity'):
        print("User is celebrity, redirecting to celebrity dashboard")
        return redirect(url_for('celebrity_dashboard'))
    
    try:
        if not supabase:
            flash('Database connection error', 'error')
            return redirect(url_for('index'))
        
        # Get user info
        user_result = supabase.table('users').select('*').eq('id', session['user_id']).execute()
        user = user_result.data[0] if user_result.data else None
        print(f"User data: {user}")
        
        # Get verified celebrities
        celebrities_result = supabase.table('users').select('*').eq('is_celebrity', True).eq('celebrity_verified', True).execute()
        celebrities = celebrities_result.data
        print(f"Found {len(celebrities)} verified celebrities")
        
        # Get user's video requests
        requests_result = supabase.table('video_requests').select('''
            *,
            celebrity:users!video_requests_celebrity_id_fkey(first_name, last_name)
        ''').eq('requester_id', session['user_id']).order('created_at', desc=True).execute()
        requests = requests_result.data
        print(f"Found {len(requests)} requests for user")
        
        return render_template('user_dashboard.html', 
                             user=user, 
                             celebrities=celebrities, 
                             requests=requests)
    except Exception as e:
        print(f"Error loading user dashboard: {e}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/celebrity-dashboard')
def celebrity_dashboard():
    """Celebrity dashboard"""
    print(f"Celebrity dashboard accessed. Session: {dict(session)}")
    
    if 'user_id' not in session or not session.get('is_celebrity'):
        print("No user_id in session or not celebrity, redirecting to login")
        return redirect(url_for('login_page'))
    
    try:
        if not supabase:
            flash('Database connection error', 'error')
            return redirect(url_for('index'))
        
        # Get celebrity info
        celebrity_result = supabase.table('users').select('*').eq('id', session['user_id']).execute()
        celebrity = celebrity_result.data[0] if celebrity_result.data else None
        print(f"Celebrity data: {celebrity}")
        
        # Get incoming requests
        requests_result = supabase.table('video_requests').select('''
            *,
            requester:users!video_requests_requester_id_fkey(first_name, last_name, email)
        ''').eq('celebrity_id', session['user_id']).order('created_at', desc=True).execute()
        requests = requests_result.data
        print(f"Found {len(requests)} requests for celebrity")
        
        return render_template('celebrity_dashboard.html', 
                             celebrity=celebrity, 
                             requests=requests)
    except Exception as e:
        print(f"Error loading celebrity dashboard: {e}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

# Test route to check if templates are accessible
@app.route('/test-template')
def test_template():
    """Test template rendering"""
    try:
        return "<h1>Template folder accessible</h1><p>Flask can serve HTML</p>"
    except Exception as e:
        return f"Template error: {str(e)}"

# ============ REST OF YOUR ROUTES ============
# (I'll include the remaining routes from your original file)

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

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return f"<h1>404 - Page Not Found</h1><p>The page you're looking for doesn't exist.</p><a href='/'>Go Home</a>", 404

@app.errorhandler(500)
def internal_error(error):
    return f"<h1>500 - Internal Server Error</h1><p>Something went wrong.</p><a href='/'>Go Home</a>", 500

if __name__ == '__main__':
    print("Starting Flask app...")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    app.run(debug=True, host='0.0.0.0', port=5000)