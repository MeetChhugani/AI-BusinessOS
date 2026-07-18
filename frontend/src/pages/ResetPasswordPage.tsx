import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '../contexts/AuthContext';
import { AlertCircle, Loader2, Key, Check } from 'lucide-react';

const resetSchema = z.object({
  token: z.string().min(1, 'Token is required'),
  new_password: z.string()
    .min(8, 'Password must be at least 8 characters long')
    .refine((val) => /[A-Z]/.test(val), { message: 'Must contain at least one uppercase letter' })
    .refine((val) => /[a-z]/.test(val), { message: 'Must contain at least one lowercase letter' })
    .refine((val) => /[0-9]/.test(val), { message: 'Must contain at least one digit' })
    .refine((val) => /[!@#$%^&*()_+\-=[\]{}|;':",./<>?`~]/.test(val), {
      message: 'Must contain at least one special character (!@#$%^&*)',
    }),
});

type ResetFormValues = z.infer<typeof resetSchema>;

export const ResetPasswordPage: React.FC = () => {
  const { resetPassword } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const tokenParam = searchParams.get('token') || '';

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<ResetFormValues>({
    resolver: zodResolver(resetSchema),
    defaultValues: {
      token: tokenParam,
    },
  });

  const watchedPassword = watch('new_password', '');

  const onSubmit = async (data: ResetFormValues) => {
    setError(null);
    try {
      await resetPassword(data);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (e: any) {
      setError(e.message || 'Failed to reset password.');
    }
  };

  const passwordCriteria = [
    { label: 'Minimum 8 characters', met: watchedPassword.length >= 8 },
    { label: 'One uppercase letter', met: /[A-Z]/.test(watchedPassword) },
    { label: 'One lowercase letter', met: /[a-z]/.test(watchedPassword) },
    { label: 'One digit', met: /[0-9]/.test(watchedPassword) },
    { label: 'One symbol (!@#$...)', met: /[!@#$%^&*()_+\-=[\]{}|;':",./<>?`~]/.test(watchedPassword) },
  ];

  if (success) {
    return (
      <div className="min-h-screen bg-background flex flex-col justify-center items-center px-4">
        <div className="w-full max-w-md glass-card rounded-2xl p-8 border border-neutral-800 text-center shadow-xl">
          <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center text-green-400 mx-auto mb-4 border border-green-500/20">
            <Check size={24} />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Password Updated</h2>
          <p className="text-sm text-muted-foreground mb-6">
            Your credentials have been successfully updated. Redirecting you to sign in...
          </p>
          <Loader2 size={24} className="animate-spin text-blue-500 mx-auto" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center px-4 relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center space-x-2 mb-4">
            <span className="text-2xl font-bold font-display tracking-tight text-white flex items-center gap-1.5">
              <span className="bg-gradient-to-r from-blue-500 to-indigo-500 w-5 h-5 rounded-md flex items-center justify-center text-xs text-white">⚡</span>
              AI Business<span className="text-blue-500">OS</span>
            </span>
          </Link>
          <h2 className="text-2xl font-bold tracking-tight text-white">Reset Credentials</h2>
          <p className="text-sm text-muted-foreground mt-2">Enter your token and set a strong new password</p>
        </div>

        <div className="glass-card rounded-2xl p-8 shadow-xl relative border border-neutral-800">
          {error && (
            <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start space-x-2 text-sm text-red-400">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Token Input */}
            <div>
              <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                Recovery Token
              </label>
              <input
                placeholder="Paste recovery token here"
                className={`w-full px-4 py-3 bg-secondary text-white rounded-lg border ${
                  errors.token ? 'border-destructive' : 'border-border'
                } focus:outline-none focus:ring-2 focus:ring-ring text-sm transition-all`}
                {...register('token')}
              />
              {errors.token && (
                <p className="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                  <AlertCircle size={12} />
                  {errors.token.message}
                </p>
              )}
            </div>

            {/* New Password Input */}
            <div>
              <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                New Password
              </label>
              <div className="relative">
                <input
                  type="password"
                  placeholder="••••••••"
                  className={`w-full pl-10 pr-4 py-3 bg-secondary text-white rounded-lg border ${
                    errors.new_password ? 'border-destructive' : 'border-border'
                  } focus:outline-none focus:ring-2 focus:ring-ring text-sm transition-all`}
                  {...register('new_password')}
                />
                <Key size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
              </div>
              {errors.new_password && (
                <p className="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                  <AlertCircle size={12} />
                  {errors.new_password.message}
                </p>
              )}
            </div>

            {/* Requirements list */}
            <div className="p-4 bg-secondary/50 rounded-lg border border-border">
              <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider block mb-2">
                Password Requirements
              </span>
              <ul className="space-y-1.5 text-xs">
                {passwordCriteria.map((c, i) => (
                  <li key={i} className="flex items-center space-x-2">
                    <span
                      className={`w-2.5 h-2.5 rounded-full flex items-center justify-center text-[8px] ${
                        c.met ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-neutral-800 text-neutral-500'
                      }`}
                    >
                      {c.met ? '✓' : ''}
                    </span>
                    <span className={c.met ? 'text-neutral-300' : 'text-muted-foreground'}>{c.label}</span>
                  </li>
                ))}
              </ul>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center py-3 bg-white text-black hover:bg-neutral-200 rounded-lg text-sm font-semibold transition-all duration-200 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 size={16} className="animate-spin mr-2" />
                  Resetting Password...
                </>
              ) : (
                'Save Password'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
