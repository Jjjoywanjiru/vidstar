from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from supabase import create_client, Client
import bcrypt
from datetime import datetime
import os
from config import Config

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Initialize Supabase client
supabase: Client = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

# Helper functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

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
    
    return render_template('dashboard.html', 
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

@app.route('/upload/<request_id>')
def upload_video(request_id):
    # This would be the page for uploading videos
    # For now, we'll just mark it as completed
    if 'user_id' not in session or not session.get('is_celebrity'):
        return redirect(url_for('login'))
    
    try:
        update_data = {
            'status': 'completed',
            'completed_at': datetime.utcnow().isoformat()
        }
        
        response = supabase.table('video_requests').update(update_data).eq('id', request_id).eq('celebrity_id', session['user_id']).execute()
        
        if response.data:
            flash('Video marked as completed!', 'success')
        else:
            flash('Error updating request.', 'error')
            
    except Exception as e:
        print(f"Upload error: {e}")
        flash('Error updating request.', 'error')
    
    return redirect(url_for('celebrity_dashboard'))

@app.route('/watch/<request_id>')
def watch_video(request_id):
    # This would be the page for watching videos
    # For now, we'll just show a placeholder
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return "Video watch page - to be implemented"

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