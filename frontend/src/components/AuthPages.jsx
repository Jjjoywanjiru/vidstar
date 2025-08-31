import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Mail, Lock, User, Phone, Calendar, MapPin, ArrowRight, Sparkles } from 'lucide-react';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = 'https://egvdtkayqkgaycryqirc.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVndmR0a2F5cWtnYXljcnlxaXJjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU3ODk5MzgsImV4cCI6MjA3MTM2NTkzOH0.z4XGkwEyFoM-4DSM5W3jPLZsqqu4m0k37ERP9ZXr37c';
const supabase = createClient(supabaseUrl, supabaseKey);

const AuthPages = () => {
  const [currentPage, setCurrentPage] = useState('login');
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
    bio: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState(null);

  // Check for existing session on component mount
  useEffect(() => {
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        console.log('Found session:', session.user);
        setUser(session.user);
        
        // Fetch additional user profile data
        const { data: profile, error: profileError } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', session.user.id)
          .single();
        
        if (profileError) {
          console.error('Profile fetch error:', profileError);
          // Profile doesn't exist, create it
          const { error: createError } = await supabase
            .from('profiles')
            .insert([{ id: session.user.id }]);
          
          if (createError) {
            console.error('Profile creation error:', createError);
          }
        } else if (profile) {
          setUser({ ...session.user, profile });
        }
      }
    };
    
    checkSession();
    
    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.id);
        
        if (session) {
          setUser(session.user);
          
          // Fetch profile data
          const { data: profile, error: profileError } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', session.user.id)
            .single();
          
          if (profileError) {
            console.error('Profile fetch error:', profileError);
          } else if (profile) {
            setUser({ ...session.user, profile });
          }
        } else {
          setUser(null);
        }
      }
    );
    
    return () => subscription.unsubscribe();
  }, []);

  // Pre-fill form when updating profile
  useEffect(() => {
    if (currentPage === 'updateProfile' && user?.profile) {
      setFormData({
        email: user.email,
        password: '',
        first_name: user.profile.first_name || '',
        last_name: user.profile.last_name || '',
        username: user.profile.username || '',
        phone: user.profile.phone || '',
        date_of_birth: user.profile.date_of_birth || '',
        country: user.profile.country || '',
        city: user.profile.city || '',
        bio: user.profile.bio || ''
      });
    }
  }, [currentPage, user]);

  // Set initial page state based on user
  useEffect(() => {
    if (user) {
      setCurrentPage('dashboard');
    }
  }, [user]);

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem',
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      position: 'relative',
      overflow: 'hidden'
    },
    mainWrapper: {
      width: '100%',
      maxWidth: '500px',
      display: 'flex',
      borderRadius: '2rem',
      overflow: 'hidden',
      boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
      backdropFilter: 'blur(10px)',
      backgroundColor: 'rgba(15, 15, 26, 0.7)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      zIndex: 10,
      position: 'relative'
    },
    formContainer: {
      width: '100%',
      padding: '3.5rem',
      background: 'rgba(15, 15, 26, 0.6)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
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
    inputIcon: {
      position: 'absolute',
      left: '1.2rem',
      top: '50%',
      transform: 'translateY(-50%)',
      color: 'rgba(255, 255, 255, 0.5)',
      width: '20px',
      height: '20px',
      transition: 'color 0.3s ease'
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
    passwordToggle: {
      position: 'absolute',
      right: '1.2rem',
      top: '50%',
      transform: 'translateY(-50%)',
      background: 'none',
      border: 'none',
      color: 'rgba(255, 255, 255, 0.5)',
      cursor: 'pointer',
      transition: 'color 0.3s ease',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    },
    errorText: {
      color: '#ff4b4b',
      fontSize: '0.9rem',
      marginTop: '0.5rem',
      marginLeft: '0.5rem'
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
      position: 'relative',
      overflow: 'hidden',
      boxShadow: '0 10px 20px rgba(101, 76, 237, 0.3)'
    },
    buttonDisabled: {
      opacity: '0.7',
      transform: 'none',
      cursor: 'not-allowed',
      boxShadow: 'none'
    },
    buttonText: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '0.5rem'
    },
    toggleText: {
      textAlign: 'center'
    },
    toggleButton: {
      background: 'none',
      border: 'none',
      color: 'rgba(255, 255, 255, 0.6)',
      cursor: 'pointer',
      transition: 'color 0.3s ease',
      fontSize: '1rem'
    },
    toggleLink: {
      background: 'linear-gradient(135deg, #654ced, #b95aee)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      fontWeight: '600'
    },
    errorBox: {
      backgroundColor: 'rgba(255, 75, 75, 0.1)',
      border: '1px solid rgba(255, 75, 75, 0.3)',
      borderRadius: '1rem',
      padding: '1.2rem',
      marginBottom: '1.8rem',
      backdropFilter: 'blur(5px)'
    },
    gridTwo: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '1.2rem',
      marginBottom: '1.8rem'
    },
    dashboardContainer: {
      width: '100%',
      maxWidth: '800px',
      padding: '2rem',
      background: 'rgba(15, 15, 26, 0.6)',
      backdropFilter: 'blur(12px)',
      borderRadius: '2rem',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      color: 'white'
    },
    logoutButton: {
      padding: '0.8rem 1.5rem',
      background: 'rgba(255, 75, 75, 0.2)',
      color: '#ff4b4b',
      border: '1px solid rgba(255, 75, 75, 0.3)',
      borderRadius: '1rem',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      fontSize: '0.9rem'
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
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
    
    if (currentPage === 'signup' || currentPage === 'createProfile' || currentPage === 'updateProfile') {
      if (!formData.first_name) newErrors.first_name = 'First name is required';
      if (!formData.last_name) newErrors.last_name = 'Last name is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setIsLoading(true);
    setErrors({});
    
    try {
      if (currentPage === 'signup') {
        // Sign up with Supabase Auth first
        const { data: authData, error: authError } = await supabase.auth.signUp({
          email: formData.email,
          password: formData.password
        });
        
        if (authError) {
          setErrors({ submit: authError.message });
          return;
        }
        
        // Update the profile that was created by the trigger
        if (authData.user) {
          console.log('Updating profile for user:', authData.user.id);
          
          // Wait a moment for the trigger to create the empty profile
          await new Promise(resolve => setTimeout(resolve, 500));
          
          const { data: profileData, error: profileError } = await supabase
            .from('profiles')
            .update({
              first_name: formData.first_name,
              last_name: formData.last_name,
              username: formData.username || null,
              phone: formData.phone || null,
              date_of_birth: formData.date_of_birth || null,
              country: formData.country || null,
              city: formData.city || null,
              bio: formData.bio || null,
              updated_at: new Date().toISOString()
            })
            .eq('id', authData.user.id)
            .select();
          
          if (profileError) {
            console.error('Profile update error:', profileError);
            setErrors({ submit: `Account created but profile setup failed: ${profileError.message}` });
            return;
          } else {
            console.log('Profile updated successfully:', profileData);
          }
        }
        
        alert('Signup successful! Please check your email to confirm your account.');
        setCurrentPage('login');
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
          bio: ''
        });
        
      } else if (currentPage === 'login') {
        // Login with Supabase Auth
        const { data, error } = await supabase.auth.signInWithPassword({
          email: formData.email,
          password: formData.password,
        });
        
        if (error) {
          setErrors({ submit: error.message });
        } else {
          setUser(data.user);
          // Profile data will be loaded by the auth state change listener
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
      setErrors({ submit: 'An unexpected error occurred. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    if (!user) return;
    
    setIsLoading(true);
    setErrors({});
    
    try {
      const profileData = {
        id: user.id,
        first_name: formData.first_name,
        last_name: formData.last_name,
        username: formData.username || null,
        phone: formData.phone || null,
        date_of_birth: formData.date_of_birth || null,
        country: formData.country || null,
        city: formData.city || null,
        bio: formData.bio || null,
        updated_at: new Date().toISOString()
      };

      const { data, error } = await supabase
        .from('profiles')
        .upsert(profileData)
        .select();
      
      if (error) {
        setErrors({ submit: error.message });
      } else {
        console.log('Profile saved:', data);
        setUser({ ...user, profile: data[0] });
        alert('Profile saved successfully!');
        setCurrentPage('dashboard');
        // Reset form
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
          bio: ''
        });
      }
    } catch (error) {
      console.error('Profile save error:', error);
      setErrors({ submit: 'Failed to save profile. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      console.error('Logout error:', error);
    } else {
      setUser(null);
      setCurrentPage('login');
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
        bio: ''
      });
    }
  };

  const InputField = ({ icon: Icon, type = 'text', name, placeholder, required = false }) => (
    <div style={styles.inputContainer}>
      <Icon style={styles.inputIcon} />
      <input
        type={name === 'password' && showPassword ? 'text' : type}
        name={name}
        placeholder={placeholder}
        value={formData[name]}
        onChange={handleInputChange}
        required={required}
        style={styles.input}
      />
      {name === 'password' && (
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          style={styles.passwordToggle}
        >
          {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
        </button>
      )}
      {errors[name] && (
        <p style={styles.errorText}>{errors[name]}</p>
      )}
    </div>
  );

  // Dashboard - shown when logged in
  if (user && currentPage === 'dashboard') {
    return (
      <div style={styles.container}>
        <div style={styles.dashboardContainer}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h1 style={styles.title}>Welcome!</h1>
            <button onClick={handleLogout} style={styles.logoutButton}>
              Logout
            </button>
          </div>
          
          <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '2rem', borderRadius: '1rem', marginBottom: '2rem' }}>
            <h2 style={{ color: 'white', marginBottom: '1rem' }}>User Information</h2>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>User ID:</strong> {user.id}</p>
            <p><strong>Email Verified:</strong> {user.email_confirmed_at ? 'Yes' : 'No'}</p>
            <p><strong>Created:</strong> {new Date(user.created_at).toLocaleDateString()}</p>
          </div>

          <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '2rem', borderRadius: '1rem' }}>
            <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', marginBottom: '1rem' }}>Profile Details</h3>
            {user.profile && (user.profile.first_name || user.profile.last_name || user.profile.username) ? (
              <div>
                {user.profile.first_name && <p><strong>Name:</strong> {user.profile.first_name} {user.profile.last_name}</p>}
                {user.profile.username && <p><strong>Username:</strong> {user.profile.username}</p>}
                {user.profile.phone && <p><strong>Phone:</strong> {user.profile.phone}</p>}
                {user.profile.country && <p><strong>Location:</strong> {user.profile.city}, {user.profile.country}</p>}
                {user.profile.date_of_birth && <p><strong>Date of Birth:</strong> {new Date(user.profile.date_of_birth).toLocaleDateString()}</p>}
                {user.profile.bio && <p><strong>Bio:</strong> {user.profile.bio}</p>}
                <button 
                  onClick={() => setCurrentPage('updateProfile')}
                  style={{...styles.button, marginTop: '1rem', marginBottom: 0}}
                >
                  Update Profile
                </button>
              </div>
            ) : (
              <div>
                <p style={{ color: 'rgba(255, 255, 255, 0.6)' }}>No profile data found.</p>
                <button 
                  onClick={() => setCurrentPage('createProfile')}
                  style={{...styles.button, marginTop: '1rem', marginBottom: 0}}
                >
                  Create Profile
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Profile creation/update form
  if (currentPage === 'createProfile' || currentPage === 'updateProfile') {
    return (
      <div style={styles.container}>
        <div style={styles.mainWrapper}>
          <div style={styles.formContainer}>
            <div>
              <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h1 style={styles.title}>{currentPage === 'updateProfile' ? 'Update Profile' : 'Create Profile'}</h1>
                <p style={styles.subtitle}>Tell us more about yourself</p>
              </div>
              
              <form onSubmit={handleProfileSubmit}>
                <div style={styles.gridTwo}>
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
                  icon={User}
                  name="username"
                  placeholder="Username (optional)"
                />
                
                <InputField
                  icon={Phone}
                  type="tel"
                  name="phone"
                  placeholder="Phone number (optional)"
                />
                
                <InputField
                  icon={Calendar}
                  type="date"
                  name="date_of_birth"
                  placeholder="Date of Birth (optional)"
                />
                
                <div style={styles.gridTwo}>
                  <InputField
                    icon={MapPin}
                    name="country"
                    placeholder="Country"
                  />
                  <InputField
                    icon={MapPin}
                    name="city"
                    placeholder="City"
                  />
                </div>
                
                <div style={styles.inputContainer}>
                  <textarea
                    name="bio"
                    placeholder="Bio (optional)"
                    value={formData.bio}
                    onChange={handleInputChange}
                    style={{
                      ...styles.input,
                      paddingLeft: '1.2rem',
                      minHeight: '100px',
                      resize: 'vertical'
                    }}
                  />
                </div>
                
                {errors.submit && (
                  <div style={styles.errorBox}>
                    <p style={{ color: '#ff4b4b', fontSize: '0.9rem', margin: 0 }}>{errors.submit}</p>
                  </div>
                )}
                
                <button
                  type="submit"
                  disabled={isLoading}
                  style={isLoading ? {...styles.button, ...styles.buttonDisabled} : styles.button}
                >
                  <span style={styles.buttonText}>
                    {isLoading ? 'Saving...' : (currentPage === 'updateProfile' ? 'Update Profile' : 'Create Profile')}
                    {!isLoading && <Sparkles size={18} />}
                  </span>
                </button>
                
                <div style={styles.toggleText}>
                  <button
                    type="button"
                    onClick={() => setCurrentPage('dashboard')}
                    style={styles.toggleButton}
                  >
                    <span style={styles.toggleLink}>Back to Dashboard</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const LoginPage = () => (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={styles.title}>Welcome Back</h1>
        <p style={styles.subtitle}>Sign in to continue your journey</p>
      </div>
      
      <form onSubmit={handleSubmit}>
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
          <div style={styles.errorBox}>
            <p style={{ color: '#ff4b4b', fontSize: '0.9rem', margin: 0 }}>{errors.submit}</p>
          </div>
        )}
        
        <button
          type="submit"
          disabled={isLoading}
          style={isLoading ? {...styles.button, ...styles.buttonDisabled} : styles.button}
        >
          <span style={styles.buttonText}>
            {isLoading ? 'Signing In...' : 'Sign In'} 
            {!isLoading && <ArrowRight size={18} />}
          </span>
        </button>
        
        <div style={styles.toggleText}>
          <button
            type="button"
            onClick={() => setCurrentPage('signup')}
            style={styles.toggleButton}
          >
            Don't have an account? <span style={styles.toggleLink}>Sign up now</span>
          </button>
        </div>
      </form>
    </div>
  );

  const SignupPage = () => (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={styles.title}>Create Account</h1>
        <p style={styles.subtitle}>Join us and start your adventure</p>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div style={styles.gridTwo}>
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
          icon={User}
          name="username"
          placeholder="Username (optional)"
        />
        
        <InputField
          icon={Lock}
          name="password"
          placeholder="Password (min 8 chars)"
          required
        />
        
        <InputField
          icon={Phone}
          type="tel"
          name="phone"
          placeholder="Phone number (optional)"
        />
        
        <InputField
          icon={Calendar}
          type="date"
          name="date_of_birth"
          placeholder="Date of Birth (optional)"
        />
        
        <div style={styles.gridTwo}>
          <InputField
            icon={MapPin}
            name="country"
            placeholder="Country"
          />
          <InputField
            icon={MapPin}
            name="city"
            placeholder="City"
          />
        </div>
        
        {errors.submit && (
          <div style={styles.errorBox}>
            <p style={{ color: '#ff4b4b', fontSize: '0.9rem', margin: 0 }}>{errors.submit}</p>
          </div>
        )}
        
        <button
          type="submit"
          disabled={isLoading}
          style={isLoading ? {...styles.button, ...styles.buttonDisabled} : styles.button}
        >
          <span style={styles.buttonText}>
            {isLoading ? 'Creating Account...' : 'Create Account'} 
            {!isLoading && <Sparkles size={18} />}
          </span>
        </button>
        
        <div style={styles.toggleText}>
          <button
            type="button"
            onClick={() => setCurrentPage('login')}
            style={styles.toggleButton}
          >
            Already have an account? <span style={styles.toggleLink}>Sign in</span>
          </button>
        </div>
      </form>
    </div>
  );

  // Set initial page state based on user
  // useEffect moved to top of component

  return (
    <div style={styles.container}>
      <div style={styles.mainWrapper}>
        <div style={styles.formContainer}>
          {currentPage === 'login' ? <LoginPage /> : <SignupPage />}
        </div>
      </div>
    </div>
  );
};

export default AuthPages;