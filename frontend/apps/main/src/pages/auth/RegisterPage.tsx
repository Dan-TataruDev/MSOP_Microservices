import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Mail, Lock, User, ArrowRight } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { validateEmail, validatePassword } from '@hospitality-platform/utils';
import type { User as UserType } from '@hospitality-platform/types';

// Helper to transform backend user to frontend User type
function transformBackendUser(backendUser: any): UserType {
  return {
    ...backendUser,
    id: String(backendUser.id),
    roles: backendUser.roles || (backendUser.role ? [backendUser.role] : ['guest']),
    preferences: backendUser.preferences || {
      notificationPreferences: {
        email: true,
        push: false,
        sms: false,
        marketing: false,
      },
      personalizationEnabled: true,
    },
    createdAt: backendUser.createdAt || backendUser.created_at || new Date().toISOString(),
    updatedAt: backendUser.updatedAt || backendUser.updated_at || new Date().toISOString(),
  };
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const { setUser, setTokens } = useAuthStore();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');

  const registerMutation = useMutation({
    mutationFn: async () => {
      if (!validateEmail(formData.email)) {
        throw new Error('Please enter a valid email address');
      }
      const passwordValidation = validatePassword(formData.password);
      if (!passwordValidation.valid) {
        throw new Error(passwordValidation.errors[0]);
      }
      if (formData.password !== formData.confirmPassword) {
        throw new Error('Passwords do not match');
      }
      return apiServices.auth.register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
      });
    },
    onSuccess: (response) => {
      try {
        // Transform backend user response to frontend User type
        const backendUser = response.data.user as any;
        const frontendUser = transformBackendUser(backendUser);
        
        setUser(frontendUser);
        setTokens(response.data.tokens);
        navigate('/');
      } catch (error) {
        console.error('Error processing registration response:', error);
        setError('Failed to process registration. Please try again.');
      }
    },
    onError: (err: any) => {
      setError(err.message || 'Registration failed. Please try again.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    registerMutation.mutate();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl mb-4 shadow-glow">
            <span className="text-white font-bold text-2xl">H</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Create Account</h1>
          <p className="text-slate-600">Join us and start exploring amazing places</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Sign Up</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
                  {error}
                </div>
              )}
              <Input
                label="Full Name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                leftIcon={<User className="w-4 h-4" />}
                placeholder="John Doe"
                required
              />
              <Input
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                leftIcon={<Mail className="w-4 h-4" />}
                placeholder="you@example.com"
                required
              />
              <Input
                label="Password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                leftIcon={<Lock className="w-4 h-4" />}
                placeholder="Create a strong password"
                required
              />
              <Input
                label="Confirm Password"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                leftIcon={<Lock className="w-4 h-4" />}
                placeholder="Confirm your password"
                required
              />
              <Button
                type="submit"
                fullWidth
                isLoading={registerMutation.isPending}
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Create Account
              </Button>
            </form>
            <div className="mt-6 text-center">
              <p className="text-sm text-slate-600">
                Already have an account?{' '}
                <Link to="/login" className="text-blue-600 font-semibold hover:text-blue-700">
                  Sign in
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

