import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Mail, Lock, ArrowRight } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { validateEmail } from '@hospitality-platform/utils';
import type { User } from '@hospitality-platform/types';

// Helper to transform backend user to frontend User type
function transformBackendUser(backendUser: any): User {
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

export default function LoginPage() {
  const navigate = useNavigate();
  const { setUser, setTokens } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const loginMutation = useMutation({
    mutationFn: async () => {
      if (!validateEmail(email)) {
        throw new Error('Please enter a valid email address');
      }
      if (password.length < 6) {
        throw new Error('Password must be at least 6 characters');
      }
      return apiServices.auth.login({ email, password });
    },
    onSuccess: (response) => {
      try {
        // Transform backend user response to frontend User type
        const backendUser = response.data.user as any;
        const frontendUser = transformBackendUser(backendUser);
        
        setUser(frontendUser);
        setTokens(response.data.tokens);
        
        // Redirect based on user role
        if (frontendUser.roles.includes('admin')) {
          navigate('/admin');
        } else if (frontendUser.roles.includes('business')) {
          navigate('/business');
        } else {
          navigate('/');
        }
      } catch (error) {
        console.error('Error processing login response:', error);
        setError('Failed to process login. Please try again.');
      }
    },
    onError: (err: any) => {
      setError(err.message || 'Login failed. Please try again.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    loginMutation.mutate();
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl mb-4 shadow-glow">
            <span className="text-white font-bold text-2xl">H</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Welcome Back</h1>
          <p className="text-slate-600">Sign in to your account to continue</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Login</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
                  {error}
                </div>
              )}
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                leftIcon={<Mail className="w-4 h-4" />}
                placeholder="you@example.com"
                required
              />
              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                leftIcon={<Lock className="w-4 h-4" />}
                placeholder="Enter your password"
                required
              />
              <Button
                type="submit"
                fullWidth
                isLoading={loginMutation.isPending}
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Sign In
              </Button>
            </form>
            <div className="mt-6 text-center">
              <p className="text-sm text-slate-600">
                Don't have an account?{' '}
                <Link to="/register" className="text-blue-600 font-semibold hover:text-blue-700">
                  Sign up
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

