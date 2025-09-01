import React, { useState } from 'react';
import { CheckCircle2, Loader2, AlertCircle, User, Mail, Lock } from 'lucide-react';
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
    outline: "bg-white text-black border border-neutral-300 hover:bg-neutral-50 focus:ring-neutral-500",
    success: "bg-green-600 text-white hover:bg-green-700 focus:ring-green-500"
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
    default: "bg-blue-50 border-blue-200 text-blue-800", 
    error: "bg-red-50 border-red-200 text-red-800", 
    success: "bg-green-50 border-green-200 text-green-800" 
  }; 
  return (
    <div className={`p-4 rounded-xl border ${variants[variant]} flex items-start gap-3`}>
      {variant === "error" && <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />} 
      {variant === "success" && <CheckCircle2 className="w-5 h-5 mt-0.5 flex-shrink-0" />}
      <div className="text-sm">{children}</div>
    </div>
  ); 
};

const RegistrationForm = ({ zipCode, onSuccess, onCancel }) => {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: ''
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
    if (!formData.email || !formData.password || !formData.first_name || !formData.last_name) {
      setError('All fields are required');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    const result = await register(formData);
    
    if (result.success) {
      // Call success callback with user data and zipCode
      onSuccess && onSuccess(result.user, zipCode);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <Card className="border-2 border-green-200 bg-green-50">
      <CardContent className="p-8">
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-green-900 mb-2">
            🎉 ZIP {zipCode} is Available!
          </h2>
          <p className="text-green-700 text-lg">
            Create your account to secure this exclusive territory
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="first_name" className="block text-sm font-medium text-neutral-700 mb-2">
                First Name
              </label>
              <div className="relative">
                <Input
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  placeholder="John"
                  error={!!error}
                  className="pl-12"
                />
                <User className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 w-4 h-4" />
              </div>
            </div>
            <div>
              <label htmlFor="last_name" className="block text-sm font-medium text-neutral-700 mb-2">
                Last Name
              </label>
              <div className="relative">
                <Input
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  placeholder="Doe"
                  error={!!error}
                  className="pl-12"
                />
                <User className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 w-4 h-4" />
              </div>
            </div>
          </div>

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
                placeholder="john@example.com"
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
                placeholder="Minimum 6 characters"
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
              variant="success"
              disabled={loading}
              className="flex-1 py-4 text-lg font-semibold"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Creating Account...
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-5 h-5" />
                  Secure ZIP {zipCode} Now
                </>
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={loading}
              className="px-6"
            >
              Cancel
            </Button>
          </div>
        </form>

        <p className="text-xs text-neutral-500 mt-4 text-center">
          By creating an account, you agree to our Terms of Service and Privacy Policy
        </p>
      </CardContent>
    </Card>
  );
};

export default RegistrationForm;