import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import client from '../../api/client';
import toast from 'react-hot-toast';
import { User, Save, Lock, Camera } from 'lucide-react';

export default function Profile() {
  const { user, updateUser } = useAuth();
  const [form, setForm] = useState({ first_name: '', last_name: '', phone: '', city: '', state: '', address: '', pincode: '' });
  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', new_password_confirm: '' });
  const [profileImage, setProfileImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pwLoading, setPwLoading] = useState(false);

  useEffect(() => {
    if (user) setForm({ first_name: user.first_name || '', last_name: user.last_name || '', phone: user.phone || '', city: user.city || '', state: user.state || '', address: user.address || '', pincode: user.pincode || '' });
  }, [user]);

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      if (profileImage) fd.append('profile_image', profileImage);
      const res = await client.patch('/auth/profile/', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      updateUser(res.data);
      toast.success('Profile updated!');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Update failed');
    } finally { setLoading(false); }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setPwLoading(true);
    try {
      await client.post('/auth/change-password/', pwForm);
      toast.success('Password changed!');
      setPwForm({ old_password: '', new_password: '', new_password_confirm: '' });
    } catch (err) {
      const data = err.response?.data;
      toast.error(data?.error || data?.old_password || data?.new_password || 'Failed');
    } finally { setPwLoading(false); }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">My Profile</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><User size={20} /> Personal Info</h2>
          <form onSubmit={handleProfileUpdate} className="space-y-4" encType="multipart/form-data">
            <div className="flex items-center gap-4 mb-4">
              <div className="relative">
                {user?.profile_image ? (
                  <img src={user.profile_image} alt="Profile" className="w-20 h-20 rounded-full object-cover" />
                ) : (
                  <div className="w-20 h-20 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-2xl font-bold">{user?.first_name?.[0]}{user?.last_name?.[0]}</div>
                )}
                <label className="absolute bottom-0 right-0 bg-primary-600 text-white p-1 rounded-full cursor-pointer hover:bg-primary-700">
                  <Camera size={14} />
                  <input type="file" accept="image/*" onChange={(e) => setProfileImage(e.target.files[0])} className="hidden" />
                </label>
              </div>
              <div>
                <p className="font-medium">{user?.first_name} {user?.last_name}</p>
                <p className="text-sm text-gray-500">{user?.email}</p>
                <p className="text-xs text-gray-400 capitalize">{user?.role?.replace('_', ' ')}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="label">First Name</label><input type="text" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} className="input-field" /></div>
              <div><label className="label">Last Name</label><input type="text" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} className="input-field" /></div>
            </div>
            <div><label className="label">Phone</label><input type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="input-field" /></div>
            <div><label className="label">City</label><input type="text" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} className="input-field" /></div>
            <div><label className="label">State</label><input type="text" value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} className="input-field" /></div>
            <div><label className="label">Address</label><textarea value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} className="input-field" rows={3} /></div>
            <div><label className="label">Pincode</label><input type="text" value={form.pincode} onChange={(e) => setForm({ ...form, pincode: e.target.value })} className="input-field" /></div>
            {profileImage && <p className="text-xs text-gray-500">New image: {profileImage.name}</p>}
            <button type="submit" disabled={loading} className="btn-primary flex items-center gap-2">
              <Save size={18} /> {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Lock size={20} /> Change Password</h2>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div><label className="label">Current Password</label><input type="password" value={pwForm.old_password} onChange={(e) => setPwForm({ ...pwForm, old_password: e.target.value })} className="input-field" required /></div>
            <div><label className="label">New Password</label><input type="password" value={pwForm.new_password} onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })} className="input-field" required /></div>
            <div><label className="label">Confirm New Password</label><input type="password" value={pwForm.new_password_confirm} onChange={(e) => setPwForm({ ...pwForm, new_password_confirm: e.target.value })} className="input-field" required /></div>
            <button type="submit" disabled={pwLoading} className="btn-primary flex items-center gap-2">
              <Lock size={18} /> {pwLoading ? 'Changing...' : 'Change Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
