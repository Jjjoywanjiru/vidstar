import React, { useState, useEffect } from 'react';
import { 
  Eye, EyeOff, Mail, Lock, User, Phone, Calendar, MapPin, 
  ArrowRight, Sparkles, Star, Heart, Video, Upload, 
  Send, MessageCircle, Play, X, Check, Users, Crown
} from 'lucide-react';

// Mock Supabase client for demonstration
const mockSupabase = {
  auth: {
    getSession: async () => ({ data: { session: null } }),
    signUp: async (credentials) => {
      console.log('Sign up:', credentials);
      return { data: { user: { id: 'user123', email: credentials.email } }, error: null };
    },
    signInWithPassword: async (credentials) => {
      console.log('Sign in:', credentials);
      return { 
        data: { 
          user: { 
            id: 'user123', 
            email: credentials.email,
            user_metadata: credentials.email === 'celebrity@test.com' ? { is_celebrity: true } : {}
          } 
        }, 
        error: null 
      };
    },
    signOut: async () => ({ error: null }),
    onAuthStateChange: (callback) => ({ data: { subscription: { unsubscribe: () => {} } } })
  },
  from: (table) => ({
    select: (fields) => ({
      eq: (column, value) => ({
        single: async () => ({ data: null, error: null }),
        execute: async () => ({ data: [], error: null })
      }),
      execute: async () => ({ data: [], error: null })
    }),
    insert: (data) => ({
      select: () => ({ execute: async () => ({ data: [data], error: null }) })
    }),
    update: (data) => ({
      eq: (column, value) => ({
        select: () => ({ execute: async () => ({ data: [data], error: null }) })
      })
    }),
    upsert: (data) => ({
      select: () => ({ execute: async () => ({ data: [data], error: null }) })
    })
  })
};

const VideoMessagingPlatform = () => {
  const [currentPage, setCurrentPage] = useState('home');
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    username: '',
    phone: '',
    date_of_birth: '',
    country: '',
    city: '',
    bio: '',
    is_celebrity: false,
    recipient_name: '',
    occasion: '',
    message_details: '',
    personal_message: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [selectedCelebrity, setSelectedCelebrity] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [shareableLink, setShareableLink] = useState('');

  // Mock data
  const [celebrities, setCelebrities] = useState([
    { id: 1, name: 'John Smith', category: 'Actor', price: 100, image: 'https://via.placeholder.com/150x150', description: 'Hollywood actor with 20+ years experience' },
    { id: 2, name: 'Sarah Johnson', category: 'Singer', price: 150, image: 'https://via.placeholder.com/150x150', description: 'Grammy award winning artist' },
    { id: 3, name: 'Mike Chen', category: 'Comedian', price: 80, image: 'https://via.placeholder.com/150x150', description: 'Stand-up comedian and TV personality' }
  ]);

  const [fanRequests, setFanRequests] = useState([
    { id: 1, fan_name: 'Alice Brown', message: 'Happy birthday message for my daughter', occasion: 'Birthday', status: 'pending', created_at: '2024-01-15' },
    { id: 2, fan_name: 'Bob Wilson', message: 'Motivational message for graduation', occasion: 'Graduation', status: 'pending', created_at: '2024-01-14' }
  ]);

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%)',
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      position: 'relative',
      overflow: 'hidden'
    },
    homeContainer: {
      display: 'flex',
      minHeight: '100vh'
    },
    homeSection: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '3rem',
      position: 'relative',
      cursor: 'pointer',
      transition: 'all 0.3s ease'
    },
    celebritySection: {
      background: 'linear-gradient(135deg, #b95aee, #654ced)',
      color: 'white'
    },
    familySection: {
      background: 'linear-gradient(135deg, #ff6b6b, #ffa726)',
      color: 'white'
    },
    sectionTitle: {
      fontSize: '3.5rem',
      fontWeight: '800',
      marginBottom: '1rem',
      textAlign: 'center'
    },
    sectionSubtitle: {
      fontSize: '1.3rem',
      opacity: 0.9,
      textAlign: 'center',
      marginBottom: '2rem'
    },
    sectionIcon: {
      width: '120px',
      height: '120px',
      marginBottom: '2rem',
      opacity: 0.8
    },
    authWrapper: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem',
      minHeight: '100vh'
    },
    authContainer: {
      width: '100%',
      maxWidth: '500px',
      padding: '3.5rem',
      background: 'rgba(15, 15, 26, 0.6)',
      backdropFilter: 'blur(12px)',
      borderRadius: '2rem',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
    },
    title: {
      fontSize: '2.8rem',
      fontWeight: '800',
      background: 'linear-gradient(135deg, #fff 0%, #b95aee 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      marginBottom: '0.5rem',
      textAlign: 'center'
    },
    subtitle: {
      color: 'rgba(255, 255, 255, 0.6)',
      textAlign: 'center',
      marginBottom: '3rem',
      fontSize: '1.1rem'
    },
    inputContainer: {
      position: 'relative',
      marginBottom: '1.8rem'
    },
    input: {
      width: '100%',
      paddingLeft: '3.5rem',
      paddingRight: '3.5rem',
      paddingTop: '1.2rem',
      paddingBottom: '1.2rem',
      backgroundColor: 'rgba(255, 255, 255, 0.03)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '1.2rem',
      color: 'white',
      fontSize: '1rem',
      outline: 'none',
      transition: 'all 0.3s ease',
      backdropFilter: 'blur(5px)',
      boxSizing: 'border-box'
    },
    inputIcon: {
      position: 'absolute',
      left: '1.2rem',
      top: '50%',
      transform: 'translateY(-50%)',
      color: 'rgba(255, 255, 255, 0.5)',
      width: '20px',
      height: '20px'
    },
    button: {
      width: '100%',
      padding: '1.2rem',
      background: 'linear-gradient(135deg, #654ced, #b95aee)',
      color: 'white',
      fontWeight: '600',
      border: 'none',
      borderRadius: '1.2rem',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      marginBottom: '2rem',
      fontSize: '1rem',
      boxShadow: '0 10px 20px rgba(101, 76, 237, 0.3)'
    },
    celebrityCard: {
      backgroundColor: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '1.5rem',
      padding: '1.5rem',
      margin: '1rem',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      backdropFilter: 'blur(10px)'
    },
    requestCard: {
      backgroundColor: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '1rem',
      padding: '1.5rem',
      margin: '0.5rem 0',
      border: '1px solid rgba(255, 255, 255, 0.1)'
    },
    modal: {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    },
    modalContent: {
      backgroundColor: 'rgba(15, 15, 26, 0.9)',
      borderRadius: '1.5rem',
      padding: '2rem',
      maxWidth: '500px',
      width: '100%',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(20px)'
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear errors when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (currentPage === 'signup' && formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    if (currentPage === 'signup') {
      if (!formData.first_name) newErrors.first_name = 'First name is required';
      if (!formData.last_name) newErrors.last_name = 'Last name is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setIsLoading(true);
    setErrors({});
    
    try {
      if (currentPage === 'signup') {
        const { data, error } = await mockSupabase.auth.signUp({
          email: formData.email,
          password: formData.password,
          options: {
            data: {
              first_name: formData.first_name,
              last_name: formData.last_name,
              is_celebrity: formData.is_celebrity
            }
          }
        });
        
        if (error) {
          setErrors({ submit: error.message });
        } else {
          alert('Signup successful! Please check your email to confirm your account.');
          setCurrentPage('login');
          resetForm();
        }
      } else if (currentPage === 'login') {
        const { data, error } = await mockSupabase.auth.signInWithPassword({
          email: formData.email,
          password: formData.password,
        });
        
        if (error) {
          setErrors({ submit: error.message });
        } else {
          setUser(data.user);
          // Route based on user type
          if (data.user.user_metadata?.is_celebrity) {
            setCurrentPage('celebrityDashboard');
          } else {
            setCurrentPage('userDashboard');
          }
        }
      }
    } catch (error) {
      setErrors({ submit: 'An unexpected error occurred. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      username: '',
      phone: '',
      date_of_birth: '',
      country: '',
      city: '',
      bio: '',
      is_celebrity: false,
      recipient_name: '',
      occasion: '',
      message_details: '',
      personal_message: ''
    });
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentPage('home');
    resetForm();
  };

  const InputField = ({ icon: Icon, type = 'text', name, placeholder, required = false }) => (
    <div style={styles.inputContainer}>
      <Icon style={styles.inputIcon} />
      <input
        type={name === 'password' && showPassword ? 'text' : type}
        name={name}
        placeholder={placeholder}
        value={formData[name] || ''}
        onChange={handleInputChange}
        required={required}
        style={styles.input}
      />
      {name === 'password' && (
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          style={{
            position: 'absolute',
            right: '1.2rem',
            top: '50%',
            transform: 'translateY(-50%)',
            background: 'none',
            border: 'none',
            color: 'rgba(255, 255, 255, 0.5)',
            cursor: 'pointer'
          }}
        >
          {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
        </button>
      )}
      {errors[name] && (
        <p style={{ color: '#ff4b4b', fontSize: '0.9rem', marginTop: '0.5rem' }}>
          {errors[name]}
        </p>
      )}
    </div>
  );

  // Homepage
  const HomePage = () => (
    <div style={styles.homeContainer}>
      <div 
        style={{...styles.homeSection, ...styles.celebritySection}}
        onClick={() => setCurrentPage('celebrityLogin')}
      >
        <Star style={styles.sectionIcon} />
        <h1 style={styles.sectionTitle}>Celebrities</h1>
        <p style={styles.sectionSubtitle}>
          Get personalized video messages from your favorite stars
        </p>
        <div style={{
          padding: '1rem 2rem',
          backgroundColor: 'rgba(255, 255, 255, 0.2)',
          borderRadius: '2rem',
          marginTop: '1rem'
        }}>
          Browse & Request Videos
        </div>
      </div>
      
      <div 
        style={{...styles.homeSection, ...styles.familySection}}
        onClick={() => setCurrentPage('familyLogin')}
      >
        <Heart style={styles.sectionIcon} />
        <h1 style={styles.sectionTitle}>Family & Friends</h1>
        <p style={styles.sectionSubtitle}>
          Send heartfelt video messages to your loved ones
        </p>
        <div style={{
          padding: '1rem 2rem',
          backgroundColor: 'rgba(255, 255, 255, 0.2)',
          borderRadius: '2rem',
          marginTop: '1rem'
        }}>
          Record & Share Videos
        </div>
      </div>
    </div>
  );

  // Celebrity Login Page
  const CelebrityLogin = () => (
    <div style={styles.authWrapper}>
      <div style={styles.authContainer}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <Crown style={{ width: '60px', height: '60px', margin: '0 auto 1rem', color: '#b95aee' }} />
          <h1 style={styles.title}>Celebrity Portal</h1>
          <p style={styles.subtitle}>Sign in to manage your fan requests</p>
        </div>
        
        <div>
          <InputField
            icon={Mail}
            type="email"
            name="email"
            placeholder="Email address"
            required
          />
          
          <InputField
            icon={Lock}
            name="password"
            placeholder="Password"
            required
          />
          
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
              <input
                type="checkbox"
                name="is_celebrity"
                checked={formData.is_celebrity}
                onChange={handleInputChange}
                style={{ marginRight: '0.5rem' }}
              />
              I am a verified celebrity
            </label>
          </div>
          
          {errors.submit && (
            <div style={{
              backgroundColor: 'rgba(255, 75, 75, 0.1)',
              border: '1px solid rgba(255, 75, 75, 0.3)',
              borderRadius: '1rem',
              padding: '1.2rem',
              marginBottom: '1.8rem'
            }}>
              <p style={{ color: '#ff4b4b', fontSize: '0.9rem', margin: 0 }}>{errors.submit}</p>
            </div>
          )}
          
          <button
            onClick={handleAuth}
            disabled={isLoading}
            style={styles.button}
          >
            {isLoading ? 'Signing In...' : 'Sign In'} <ArrowRight size={18} />
          </button>
        </div>
        
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={() => setCurrentPage('home')}
            style={{
              background: 'none',
              border: 'none',
              color: 'rgba(255, 255, 255, 0.6)',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );

  // Family Login Page
  const FamilyLogin = () => (
    <div style={styles.authWrapper}>
      <div style={styles.authContainer}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <Heart style={{ width: '60px', height: '60px', margin: '0 auto 1rem', color: '#ff6b6b' }} />
          <h1 style={styles.title}>Family & Friends</h1>
          <p style={styles.subtitle}>Share precious moments with loved ones</p>
        </div>
        
        <div>
          <InputField
            icon={Mail}
            type="email"
            name="email"
            placeholder="Email address"
            required
          />
          
          <InputField
            icon={Lock}
            name="password"
            placeholder="Password"
            required
          />
          
          {errors.submit && (
            <div style={{
              backgroundColor: 'rgba(255, 75, 75, 0.1)',
              border: '1px solid rgba(255, 75, 75, 0.3)',
              borderRadius: '1rem',
              padding: '1.2rem',
              marginBottom: '1.8rem'
            }}>
              <p style={{ color: '#ff4b4b', fontSize: '0.9rem', margin: 0 }}>{errors.submit}</p>
            </div>
          )}
          
          <button
            onClick={handleAuth}
            disabled={isLoading}
            style={styles.button}
          >
            {isLoading ? 'Signing In...' : 'Sign In'} <ArrowRight size={18} />
          </button>
        </div>
        
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <button
            onClick={() => setCurrentPage('signup')}
            style={{
              background: 'none',
              border: 'none',
              color: 'rgba(255, 255, 255, 0.6)',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Don't have an account? <span style={{ color: '#ff6b6b' }}>Sign up</span>
          </button>
        </div>
        
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={() => setCurrentPage('home')}
            style={{
              background: 'none',
              border: 'none',
              color: 'rgba(255, 255, 255, 0.6)',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );

  // Signup Page
  const SignupPage = () => (
    <div style={styles.authWrapper}>
      <div style={styles.authContainer}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={styles.title}>Join Us</h1>
          <p style={styles.subtitle}>Create your account to get started</p>
        </div>
        
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.2rem' }}>
            <InputField
              icon={User}
              name="first_name"
              placeholder="First Name"
              required
            />
            <InputField
              icon={User}
              name="last_name"
              placeholder="Last Name"
              required
            />
          </div>
          
          <InputField
            icon={Mail}
            type="email"
            name="email"
            placeholder="Email address"
            required
          />
          
          <InputField
            icon={Lock}
            name="password"
            placeholder="Password (min 8 chars)"
            required
          />
          
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
              <input
                type="checkbox"
                name="is_celebrity"
                checked={formData.is_celebrity}
                onChange={handleInputChange}
                style={{ marginRight: '0.5rem' }}
              />
              I am a celebrity applying for verification
            </label>
          </div>
          
          {errors.submit && (
            <div style={{
              backgroundColor: 'rgba(255, 75, 75, 0.1)',
              border: '1px solid rgba(255, 75, 75, 0.3)',
              borderRadius: '1rem',
              padding: '1.2rem',
              marginBottom: '1.8rem'
            }}>
              <p style={{ color: '#ff4b4b', fontSize: '0.9rem', margin: 0 }}>{errors.submit}</p>
            </div>
          )}
          
          <button
            onClick={handleAuth}
            disabled={isLoading}
            style={styles.button}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'} <Sparkles size={18} />
          </button>
        </div>
        
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={() => setCurrentPage('familyLogin')}
            style={{
              background: 'none',
              border: 'none',
              color: 'rgba(255, 255, 255, 0.6)',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Already have an account? <span style={{ color: '#b95aee' }}>Sign in</span>
          </button>
        </div>
      </div>
    </div>
  );

  // Celebrity Dashboard
  const CelebrityDashboard = () => (
    <div style={styles.authWrapper}>
      <div style={{ ...styles.authContainer, maxWidth: '800px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1 style={styles.title}>Celebrity Dashboard</h1>
          <button onClick={handleLogout} style={{
            padding: '0.8rem 1.5rem',
            background: 'rgba(255, 75, 75, 0.2)',
            color: '#ff4b4b',
            border: '1px solid rgba(255, 75, 75, 0.3)',
            borderRadius: '1rem',
            cursor: 'pointer'
          }}>
            Logout
          </button>
        </div>
        
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ color: 'white', marginBottom: '1rem' }}>Fan Requests</h2>
          {fanRequests.map(request => (
            <div key={request.id} style={styles.requestCard}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ color: 'white' }}>
                  <h3 style={{ margin: '0 0 0.5rem 0' }}>{request.fan_name}</h3>
                  <p style={{ margin: '0 0 0.5rem 0', opacity: 0.8 }}>{request.occasion}</p>
                  <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.7 }}>{request.message}</p>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button 
                    onClick={() => setCurrentPage('recordVideo')}
                    style={{
                      padding: '0.5rem 1rem',
                      background: 'linear-gradient(135deg, #4caf50, #45a049)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      fontSize: '0.8rem'
                    }}
                  >
                    <Video size={16} style={{ marginRight: '0.5rem' }} />
                    Record
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // User Dashboard (for fans and family)
  const UserDashboard = () => (
    <div style={styles.authWrapper}>
      <div style={{ ...styles.authContainer, maxWidth: '800px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1 style={styles.title}>Dashboard</h1>
          <button onClick={handleLogout} style={{
            padding: '0.8rem 1.5rem',
            background: 'rgba(255, 75, 75, 0.2)',
            color: '#ff4b4b',
            border: '1px solid rgba(255, 75, 75, 0.3)',
            borderRadius: '1rem',
            cursor: 'pointer'
          }}>
            Logout
          </button>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          <div style={{
            padding: '2rem',
            backgroundColor: 'rgba(185, 90, 238, 0.1)',
            borderRadius: '1.5rem',
            border: '1px solid rgba(185, 90, 238, 0.3)',
            textAlign: 'center',
            cursor: 'pointer'
          }} onClick={() => setCurrentPage('celebrityBrowse')}>
            <Star style={{ width: '60px', height: '60px', margin: '0 auto 1rem', color: '#b95aee' }} />
            <h3 style={{ color: 'white', marginBottom: '0.5rem' }}>Celebrity Videos</h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem' }}>
              Request personalized videos from celebrities
            </p>
          </div>
          
          <div style={{
            padding: '2rem',
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            borderRadius: '1.5rem',
            border: '1px solid rgba(255, 107, 107, 0.3)',
            textAlign: 'center',
            cursor: 'pointer'
          }} onClick={() => setCurrentPage('familyRecord')}>
            <Video style={{ width: '60px', height: '60px', margin: '0 auto 1rem', color: '#ff6b6b' }} />
            <h3 style={{ color: 'white', marginBottom: '0.5rem' }}>Family Videos</h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem' }}>
              Record and share videos with family & friends
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  // Celebrity Browse Page
  const CelebrityBrowse = () => (
    <div style={styles.authWrapper}>
      <div style={{ ...styles.authContainer, maxWidth: '1000px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1 style={styles.title}>Choose a Celebrity</h1>
          <button onClick={() => setCurrentPage('userDashboard')} style={{
            padding: '0.8rem 1.5rem',
            background: 'rgba(255, 255, 255, 0.1)',
            color: 'white',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '1rem',
            cursor: 'pointer'
          }}>
            ← Back
          </button>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          {celebrities.map(celebrity => (
            <div 
              key={celebrity.id} 
              style={styles.celebrityCard}
              onClick={() => {
                setSelectedCelebrity(celebrity);
                setCurrentPage('requestForm');
              }}
            >
              <img 
                src={celebrity.image} 
                alt={celebrity.name}
                style={{ width: '100%', height: '200px', objectFit: 'cover', borderRadius: '1rem', marginBottom: '1rem' }}
              />
              <h3 style={{ color: 'white', margin: '0 0 0.5rem 0' }}>{celebrity.name}</h3>
              <p style={{ color: 'rgba(255, 255, 255, 0.7)', margin: '0 0 0.5rem 0' }}>{celebrity.category}</p>
              <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', margin: '0 0 1rem 0' }}>{celebrity.description}</p>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '1rem',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '0.5rem'
              }}>
                <span style={{ color: 'white', fontWeight: '600' }}>${celebrity.price}</span>
                <span style={{ color: '#4caf50', fontSize: '0.9rem' }}>Available</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Request Form for Celebrity Videos
  const RequestForm = () => (
    <div style={styles.authWrapper}>
      <div style={styles.authContainer}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={styles.title}>Request Video</h1>
          <p style={styles.subtitle}>Tell {selectedCelebrity?.name} about your request</p>
        </div>
        
        <div>
          <InputField
            icon={User}
            name="recipient_name"
            placeholder="Who is this video for?"
            required
          />
          
          <InputField
            icon={Calendar}
            name="occasion"
            placeholder="What's the occasion?"
            required
          />
          
          <div style={styles.inputContainer}>
            <textarea
              name="message_details"
              placeholder="Provide details about what you'd like the celebrity to say..."
              value={formData.message_details || ''}
              onChange={handleInputChange}
              style={{
                ...styles.input,
                paddingLeft: '1.2rem',
                minHeight: '120px',
                resize: 'vertical'
              }}
              required
            />
          </div>
          
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            padding: '1.5rem',
            borderRadius: '1rem',
            marginBottom: '2rem'
          }}>
            <h3 style={{ color: 'white', margin: '0 0 1rem 0' }}>Order Summary</h3>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'rgba(255, 255, 255, 0.8)' }}>
              <span>{selectedCelebrity?.name} video message</span>
              <span>${selectedCelebrity?.price}</span>
            </div>
          </div>
          
          <button 
            onClick={(e) => {
              e.preventDefault();
              alert('Request sent successfully!');
              setCurrentPage('userDashboard');
            }}
            style={styles.button}
          >
            Send Request <Send size={18} />
          </button>
        </div>
        
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={() => setCurrentPage('celebrityBrowse')}
            style={{
              background: 'none',
              border: 'none',
              color: 'rgba(255, 255, 255, 0.6)',
              cursor: 'pointer'
            }}
          >
            ← Back to Celebrities
          </button>
        </div>
      </div>
    </div>
  );

  // Family Video Recording Page
  const FamilyRecord = () => (
    <div style={styles.authWrapper}>
      <div style={styles.authContainer}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={styles.title}>Record Video</h1>
          <p style={styles.subtitle}>Create a special message for someone you love</p>
        </div>
        
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '1.5rem',
          padding: '3rem',
          textAlign: 'center',
          marginBottom: '2rem',
          border: '2px dashed rgba(255, 255, 255, 0.2)'
        }}>
          <Video style={{ width: '80px', height: '80px', margin: '0 auto 1rem', color: 'rgba(255, 255, 255, 0.5)' }} />
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '1.5rem' }}>
            Click to start recording your video message
          </p>
          <button style={{
            ...styles.button,
            maxWidth: '200px',
            margin: '0 auto'
          }}>
            <Video size={18} style={{ marginRight: '0.5rem' }} />
            Start Recording
          </button>
        </div>
        
        <div style={{ marginBottom: '2rem' }}>
          <label style={{ color: 'white', display: 'block', marginBottom: '0.5rem' }}>
            Add a personal message (optional):
          </label>
          <textarea
            name="personal_message"
            placeholder="Write something special to go with your video..."
            value={formData.personal_message || ''}
            onChange={handleInputChange}
            style={{
              ...styles.input,
              paddingLeft: '1.2rem',
              minHeight: '100px',
              resize: 'vertical'
            }}
          />
        </div>
        
        <button 
          onClick={() => {
            const link = `${window.location.origin}/watch/abc123`;
            setShareableLink(link);
            setCurrentPage('shareVideo');
          }}
          style={styles.button}
        >
          Generate Shareable Link <Send size={18} />
        </button>
        
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={() => setCurrentPage('userDashboard')}
            style={{
              background: 'none',
              border: 'none',
              color: 'rgba(255, 255, 255, 0.6)',
              cursor: 'pointer'
            }}
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );

  // Share Video Page
  const ShareVideo = () => (
    <div style={styles.authWrapper}>
      <div style={styles.authContainer}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={styles.title}>Video Ready!</h1>
          <p style={styles.subtitle}>Share your video with family and friends</p>
        </div>
        
        <div style={{
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          border: '1px solid rgba(76, 175, 80, 0.3)',
          borderRadius: '1rem',
          padding: '1.5rem',
          marginBottom: '2rem'
        }}>
          <Check style={{ color: '#4caf50', margin: '0 auto 1rem', display: 'block' }} size={40} />
          <p style={{ color: '#4caf50', textAlign: 'center', margin: 0 }}>
            Your video has been uploaded successfully!
          </p>
        </div>
        
        <div style={{ marginBottom: '2rem' }}>
          <label style={{ color: 'white', display: 'block', marginBottom: '0.5rem' }}>
            Shareable Link:
          </label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              value={shareableLink}
              readOnly
              style={{
                ...styles.input,
                paddingLeft: '1rem',
                flex: 1
              }}
            />
            <button
              onClick={() => navigator.clipboard.writeText(shareableLink)}
              style={{
                padding: '1.2rem',
                background: 'linear-gradient(135deg, #654ced, #b95aee)',
                color: 'white',
                border: 'none',
                borderRadius: '1rem',
                cursor: 'pointer'
              }}
            >
              Copy
            </button>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
          <button style={{
            ...styles.button,
            margin: 0,
            background: 'linear-gradient(135deg, #25d366, #128c7e)'
          }}>
            <MessageCircle size={18} style={{ marginRight: '0.5rem' }} />
            Share on WhatsApp
          </button>
          <button style={{
            ...styles.button,
            margin: 0,
            background: 'linear-gradient(135deg, #1da1f2, #0d8bd9)'
          }}>
            <Send size={18} style={{ marginRight: '0.5rem' }} />
            Share via SMS
          </button>
        </div>
        
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={() => setCurrentPage('userDashboard')}
            style={{
              background: 'none',
              border: 'none',
              color: 'rgba(255, 255, 255, 0.6)',
              cursor: 'pointer'
            }}
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );

  // Video Recording Page for Celebrities
  const RecordVideoPage = () => (
    <div style={styles.authWrapper}>
      <div style={styles.authContainer}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={styles.title}>Record Response</h1>
          <p style={styles.subtitle}>Record your personalized video message</p>
        </div>
        
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '1.5rem',
          padding: '2rem',
          marginBottom: '2rem'
        }}>
          <h3 style={{ color: 'white', marginBottom: '1rem' }}>Request Details</h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.8)', marginBottom: '0.5rem' }}>
            <strong>For:</strong> Sarah's 25th Birthday
          </p>
          <p style={{ color: 'rgba(255, 255, 255, 0.8)', marginBottom: '0.5rem' }}>
            <strong>Occasion:</strong> Birthday
          </p>
          <p style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
            <strong>Message:</strong> Please wish Sarah a happy 25th birthday and tell her to keep pursuing her dreams!
          </p>
        </div>
        
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '1.5rem',
          padding: '3rem',
          textAlign: 'center',
          marginBottom: '2rem',
          border: '2px dashed rgba(255, 255, 255, 0.2)'
        }}>
          <Video style={{ width: '80px', height: '80px', margin: '0 auto 1rem', color: 'rgba(255, 255, 255, 0.5)' }} />
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '1.5rem' }}>
            Record your personalized video response
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button style={{
              ...styles.button,
              maxWidth: '150px',
              margin: 0,
              background: 'linear-gradient(135deg, #ff4757, #ff3742)'
            }}>
              <Video size={18} />
              Record
            </button>
            <button style={{
              ...styles.button,
              maxWidth: '150px',
              margin: 0,
              background: 'rgba(255, 255, 255, 0.1)'
            }}>
              <Upload size={18} />
              Upload
            </button>
          </div>
        </div>
        
        <button 
          onClick={() => {
            alert('Video sent successfully!');
            setCurrentPage('celebrityDashboard');
          }}
          style={styles.button}
        >
          Send Video to Fan <Send size={18} />
        </button>
        
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={() => setCurrentPage('celebrityDashboard')}
            style={{
              background: 'none',
              border: 'none',
              color: 'rgba(255, 255, 255, 0.6)',
              cursor: 'pointer'
            }}
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );

  // Render appropriate page
  const renderPage = () => {
    switch(currentPage) {
      case 'home':
        return <HomePage />;
      case 'celebrityLogin':
        return <CelebrityLogin />;
      case 'familyLogin':
        return <FamilyLogin />;
      case 'signup':
        return <SignupPage />;
      case 'celebrityDashboard':
        return <CelebrityDashboard />;
      case 'userDashboard':
        return <UserDashboard />;
      case 'celebrityBrowse':
        return <CelebrityBrowse />;
      case 'requestForm':
        return <RequestForm />;
      case 'familyRecord':
        return <FamilyRecord />;
      case 'shareVideo':
        return <ShareVideo />;
      case 'recordVideo':
        return <RecordVideoPage />;
      default:
        return <HomePage />;
    }
  };

  return (
    <div style={styles.container}>
      {renderPage()}
    </div>
  );
};

export default VideoMessagingPlatform;