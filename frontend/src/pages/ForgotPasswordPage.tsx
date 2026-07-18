import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '../contexts/AuthContext';
import { AlertCircle, Loader2, Mail, CheckCircle2 } from 'lucide-react';

const forgotSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

type ForgotFormValues = z.infer<typeof forgotSchema>;

export const ForgotPasswordPage: React.FC = () => {
  const { forgotPassword } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotFormValues>({
    resolver: zodResolver(forgotSchema),
  });

  const onSubmit = async (data: ForgotFormValues) => {
    setError(null);
    setSuccess(null);
    try {
      await forgotPassword(data.email);
      setSuccess('Recovery link dispatched! If the email is registered, you will receive reset instructions.');
    } catch (e: any) {
      setError(e.message || 'Recovery request failed.');
    }
  };

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
          <h2 className="text-2xl font-bold tracking-tight text-white">Reset Password</h2>
          <p className="text-sm text-muted-foreground mt-2">Recover your credentials to access your ERP dashboard</p>
        </div>

        <div className="glass-card rounded-2xl p-8 shadow-xl relative border border-neutral-800">
          {error && (
            <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start space-x-2 text-sm text-red-400">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {success ? (
            <div className="text-center py-4">
              <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center text-green-400 mx-auto mb-4 border border-green-500/20">
                <CheckCircle2 size={20} />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Check your email</h3>
              <p className="text-sm text-muted-foreground leading-relaxed mb-6">{success}</p>
              <Link
                to="/login"
                className="inline-flex w-full items-center justify-center py-2.5 bg-neutral-800 text-white rounded-lg text-sm font-semibold hover:bg-neutral-700 transition"
              >
                Back to Login
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    placeholder="name@company.com"
                    className={`w-full pl-10 pr-4 py-3 bg-secondary text-white rounded-lg border ${
                      errors.email ? 'border-destructive' : 'border-border'
                    } focus:outline-none focus:ring-2 focus:ring-ring text-sm transition-all`}
                    {...register('email')}
                  />
                  <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
                </div>
                {errors.email && (
                  <p className="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                    <AlertCircle size={12} />
                    {errors.email.message}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center py-3 bg-white text-black hover:bg-neutral-200 rounded-lg text-sm font-semibold transition-all duration-200 disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 size={16} className="animate-spin mr-2" />
                    Requesting link...
                  </>
                ) : (
                  'Send Reset Link'
                )}
              </button>
            </form>
          )}
        </div>

        {!success && (
          <p className="text-center text-sm text-muted-foreground mt-6">
            Remembered your credentials?{' '}
            <Link to="/login" className="text-white hover:underline">
              Log in
            </Link>
          </p>
        )}
      </div>
    </div>
  );
};
