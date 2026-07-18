import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '../contexts/AuthContext';
import { AlertCircle, Loader2, Check } from 'lucide-react';

const NAME_REGEX = /^[a-zA-Z\s\-']+$/;
const PHONE_REGEX = /^\+?[1-9]\d{1,14}$/;

const registerSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  full_name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters')
    .refine((val) => NAME_REGEX.test(val), {
      message: 'Name can only contain alphabetic letters, spaces, hyphens, and apostrophes',
    }),
  phone: z.string()
    .optional()
    .or(z.literal(''))
    .refine((val) => !val || PHONE_REGEX.test(val), {
      message: 'Phone number must match international format (e.g. +1234567890)',
    }),
  company_name: z.string().optional().or(z.literal('')),
  password: z.string()
    .min(8, 'Password must be at least 8 characters long')
    .refine((val) => /[A-Z]/.test(val), { message: 'Must contain at least one uppercase letter' })
    .refine((val) => /[a-z]/.test(val), { message: 'Must contain at least one lowercase letter' })
    .refine((val) => /[0-9]/.test(val), { message: 'Must contain at least one digit' })
    .refine((val) => /[!@#$%^&*()_+\-=[\]{}|;':",./<>?`~]/.test(val), {
      message: 'Must contain at least one special character (!@#$%^&*)',
    }),
  role: z.enum(['SUPER_ADMIN', 'ADMIN', 'MANAGER', 'HR', 'FINANCE', 'SALES', 'EMPLOYEE'], {
    errorMap: () => ({ message: 'Please select a valid role' }),
  }),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export const RegisterPage: React.FC = () => {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      role: 'EMPLOYEE',
    },
  });

  const watchedPassword = watch('password', '');

  const onSubmit = async (data: RegisterFormValues) => {
    setError(null);
    try {
      // Clean empty values
      const cleanedData = {
        ...data,
        phone: data.phone || undefined,
        company_name: data.company_name || undefined,
      };
      await registerUser(cleanedData);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (e: any) {
      setError(e.message || 'Registration failed. Please check your details.');
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
          <h2 className="text-2xl font-bold text-white mb-2">Registration Successful</h2>
          <p className="text-sm text-muted-foreground mb-6">
            Your account has been created. Redirecting you to the login screen...
          </p>
          <Loader2 size={24} className="animate-spin text-blue-500 mx-auto" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center px-4 py-12 relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-xl">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center space-x-2 mb-4">
            <span className="text-2xl font-bold font-display tracking-tight text-white flex items-center gap-1.5">
              <span className="bg-gradient-to-r from-blue-500 to-indigo-500 w-5 h-5 rounded-md flex items-center justify-center text-xs text-white">⚡</span>
              AI Business<span className="text-blue-500">OS</span>
            </span>
          </Link>
          <h2 className="text-2xl font-bold tracking-tight text-white">Create your developer account</h2>
          <p className="text-sm text-muted-foreground mt-2">Initialize the SaaS ERP system foundation</p>
        </div>

        <div className="glass-card rounded-2xl p-8 shadow-xl relative border border-neutral-800">
          {error && (
            <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start space-x-2 text-sm text-red-400">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Full Name */}
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Full Name
                </label>
                <input
                  placeholder="John Doe"
                  className="w-full px-4 py-3 bg-secondary text-white rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring text-sm transition-all"
                  {...register('full_name')}
                />
                {errors.full_name && (
                  <p className="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                    <AlertCircle size={12} />
                    {errors.full_name.message}
                  </p>
                )}
              </div>

              {/* Email */}
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  placeholder="name@company.com"
                  className="w-full px-4 py-3 bg-secondary text-white rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring text-sm transition-all"
                  {...register('email')}
                />
                {errors.email && (
                  <p className="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                    <AlertCircle size={12} />
                    {errors.email.message}
                  </p>
                )}
              </div>

              {/* Phone (E.164) */}
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Phone Number (Optional)
                </label>
                <input
                  placeholder="+15555551234"
                  className="w-full px-4 py-3 bg-secondary text-white rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring text-sm transition-all"
                  {...register('phone')}
                />
                {errors.phone && (
                  <p className="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                    <AlertCircle size={12} />
                    {errors.phone.message}
                  </p>
                )}
              </div>

              {/* Company Name */}
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Company Name (Optional)
                </label>
                <input
                  placeholder="AI BusinessOS Corp"
                  className="w-full px-4 py-3 bg-secondary text-white rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring text-sm transition-all"
                  {...register('company_name')}
                />
              </div>

              {/* Role dropdown selection */}
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Assign System Role
                </label>
                <select
                  className="w-full px-4 py-3 bg-secondary text-white rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring text-sm transition-all"
                  {...register('role')}
                >
                  <option value="SUPER_ADMIN">Super Admin</option>
                  <option value="ADMIN">Admin</option>
                  <option value="MANAGER">Manager</option>
                  <option value="HR">HR Specialist</option>
                  <option value="FINANCE">Finance Expert</option>
                  <option value="SALES">Sales Agent</option>
                  <option value="EMPLOYEE">Employee</option>
                </select>
                {errors.role && (
                  <p className="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                    <AlertCircle size={12} />
                    {errors.role.message}
                  </p>
                )}
              </div>

              {/* Password */}
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Password
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  className="w-full px-4 py-3 bg-secondary text-white rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring text-sm transition-all"
                  {...register('password')}
                />
                {errors.password && (
                  <p className="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                    <AlertCircle size={12} />
                    {errors.password.message}
                  </p>
                )}
              </div>
            </div>

            {/* Password strength visualizer checklist */}
            <div className="mt-4 p-4 bg-secondary/50 rounded-lg border border-border">
              <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider block mb-2">
                Password Requirements
              </span>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {passwordCriteria.map((c, i) => (
                  <li key={i} className="flex items-center space-x-2">
                    <span
                      className={`w-3 h-3 rounded-full flex items-center justify-center text-[9px] ${
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
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-sm text-muted-foreground mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-white hover:underline">
            Log in here
          </Link>
        </p>
      </div>
    </div>
  );
};
