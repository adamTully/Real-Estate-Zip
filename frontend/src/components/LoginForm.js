import React, { useState } from 'react';
import { Loader2, AlertCircle, Mail, Lock, LogIn } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Card = ({ className = "", children, ...props }) => (
  <div className={`rounded-2xl shadow-lg border border-neutral-200 bg-white ${className}`} {...props}>
    {children}
  </div>
);

const CardContent = ({ className = "", children }) => (
  <div className={`p-5 md:p-6 ${className}`}>
    {children}
  </div>
);

const Button = ({ className = "", variant = "default", children, disabled, ...props }) => {
  const baseClasses = "inline-flex items-center justify-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  const variants = { 
    default: "bg-black text-white hover:bg-neutral-800 focus:ring-black disabled:bg-neutral-300", 
    outline: "bg-white text-black border border-neutral-300 hover:bg-neutral-50 focus:ring-neutral-500"
  };
  return (
    <button 
      className={`${baseClasses} ${variants[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`} 
      disabled={disabled} 
      {...props}
    >
      {children}
    </button>
  );
};

const Input = ({ className = "", error, ...props }) => (
  <input 
    className={`w-full rounded-xl border px-4 py-3 text-base outline-none focus:ring-4 focus:ring-black/5 ${error ? 'border-red-300 focus:ring-red-100' : 'border-neutral-300'} ${className}`} 
    {...props} 
  />
);

const Alert = ({ variant = "default", children }) => { 
  const variants = { 
    error: "bg-red-50 border-red-200 text-red-800"
  }; 
  return (
    <div className={`p-4 rounded-xl border ${variants[variant]} flex items-start gap-3`}>
      <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
      <div className="text-sm">{children}</div>
    </div>
  ); 
};

const LoginForm = ({ onSuccess, onCancel }) => {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Basic validation
    if (!formData.email || !formData.password) {
      setError('Email and password are required');
      setLoading(false);
      return;
    }

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      onSuccess && onSuccess(result.user);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <Card className="border-2 border-blue-200 bg-blue-50">
      <CardContent className="p-8">
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <LogIn className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-blue-900 mb-2">
            Welcome Back
          </h2>
          <p className="text-blue-700">
            Sign in to access your exclusive territories
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-2">
              Email Address
            </label>
            <div className="relative">
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Enter your email"
                error={!!error}
                className="pl-12"
              />
              <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 w-4 h-4" />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-neutral-700 mb-2">
              Password
            </label>
            <div className="relative">
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                error={!!error}
                className="pl-12"
              />
              <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 w-4 h-4" />
            </div>
          </div>

          {error && <Alert variant="error">{error}</Alert>}

          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 py-4 text-lg font-semibold"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Signing In...
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  Sign In
                </>
              )}
            </Button>
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={loading}
                className="px-6"
              >
                Cancel
              </Button>
            )}
          </div>
        </form>

        <div className="text-center mt-6 pt-6 border-t border-neutral-200">
          <p className="text-sm text-neutral-600">
            Don't have an account? <button className="text-blue-600 hover:text-blue-700 font-medium">Sign up here</button>
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default LoginForm;