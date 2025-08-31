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
    city: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

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
      backdropFilter: 'blur(5px)'
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
    
    if (currentPage === 'signup') {
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
    
    try {
      if (currentPage === 'signup') {
        // Sign up with Supabase Auth
        const { data: authData, error: authError } = await supabase.auth.signUp({
          email: formData.email,
          password: formData.password,
        });
        
        if (authError) {
          setErrors({ submit: authError.message });
          return;
        }
        
        // If signup successful, add user to the users table
        const { data: userData, error: userError } = await supabase
          .from('users')
          .insert([
            {
              id: authData.user.id,
              email: formData.email,
              first_name: formData.first_name,
              last_name: formData.last_name,
              username: formData.username,
              phone: formData.phone,
              date_of_birth: formData.date_of_birth,
              country: formData.country,
              city: formData.city
            }
          ]);
        
        if (userError) {
          setErrors({ submit: userError.message });
        } else {
          alert('Signup successful! Please check your email to confirm your account.');
          setCurrentPage('login');
        }
      } else {
        // Login with Supabase Auth
        const { data, error } = await supabase.auth.signInWithPassword({
          email: formData.email,
          password: formData.password,
        });
        
        if (error) {
          setErrors({ submit: error.message });
        } else {
          alert('Login successful!');
          console.log('User data:', data);
          // You can redirect the user or set user state here
        }
      }
    } catch (error) {
      setErrors({ submit: 'An error occurred. Please try again.' });
    } finally {
      setIsLoading(false);
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

  const LoginPage = () => (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={styles.title}>Welcome Back</h1>
        <p style={styles.subtitle}>Sign in to continue your journey</p>
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
          <div style={styles.errorBox}>
            <p style={{ color: '#ff4b4b', fontSize: '0.9rem', margin: 0 }}>{errors.submit}</p>
          </div>
        )}
        
        <button
          onClick={handleSubmit}
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
      </div>
    </div>
  );

  const SignupPage = () => (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={styles.title}>Create Account</h1>
        <p style={styles.subtitle}>Join us and start your adventure</p>
      </div>
      
      <div>
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
          onClick={handleSubmit}
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
      </div>
    </div>
  );

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