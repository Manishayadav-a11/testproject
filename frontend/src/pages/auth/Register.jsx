import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, User, Phone } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';

export default function Register() {
  const [form, setForm] = useState({ email: '', password: '', password_confirm: '', first_name: '', last_name: '', phone: '', role: 'student' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: '' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    try {
      await register(form);
      toast.success('Account created successfully!');
      const dashMap = { student: '/dashboard/student', institute_owner: '/dashboard/institute', instructor: '/dashboard/institute' };
      navigate(dashMap[form.role] || '/');
    } catch (err) {
      if (err.response?.data) setErrors(err.response.data);
      else toast.error('Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-128px)] flex items-center justify-center py-12 px-4">
      <div className="card max-w-lg w-full">
        <h2 className="text-2xl font-bold text-center mb-6">Create Account</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">First Name</label>
              <div className="relative">
                <User size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="text" name="first_name" value={form.first_name} onChange={handleChange} className="input-field pl-10" required />
              </div>
              {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name}</p>}
            </div>
            <div>
              <label className="label">Last Name</label>
              <input type="text" name="last_name" value={form.last_name} onChange={handleChange} className="input-field" required />
              {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name}</p>}
            </div>
          </div>
          <div>
            <label className="label">Email</label>
            <div className="relative">
              <Mail size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input type="email" name="email" value={form.email} onChange={handleChange} className="input-field pl-10" required />
            </div>
            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
          </div>
          <div>
            <label className="label">Phone</label>
            <div className="relative">
              <Phone size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input type="tel" name="phone" value={form.phone} onChange={handleChange} className="input-field pl-10" placeholder="+91 XXXXX XXXXX" />
            </div>
          </div>
          <div>
            <label className="label">I am a</label>
            <select name="role" value={form.role} onChange={handleChange} className="input-field">
              <option value="student">Student</option>
              <option value="institute_owner">Institute Owner</option>
              <option value="instructor">Instructor</option>
            </select>
          </div>
          <div>
            <label className="label">Password</label>
            <div className="relative">
              <Lock size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input type={showPassword ? 'text' : 'password'} name="password" value={form.password} onChange={handleChange} className="input-field pl-10 pr-10" required />
              <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.password && <p className="text-red-500 text-xs mt-1">{Array.isArray(errors.password) ? errors.password.join(', ') : errors.password}</p>}
          </div>
          <div>
            <label className="label">Confirm Password</label>
            <div className="relative">
              <Lock size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input type="password" name="password_confirm" value={form.password_confirm} onChange={handleChange} className="input-field pl-10" required />
            </div>
            {errors.password_confirm && <p className="text-red-500 text-xs mt-1">{errors.password_confirm}</p>}
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p className="text-center mt-6 text-sm text-gray-600">
          Already have an account? <Link to="/login" className="text-primary-600 hover:underline font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
