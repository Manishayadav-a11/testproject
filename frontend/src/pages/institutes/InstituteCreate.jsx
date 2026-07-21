import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import toast from 'react-hot-toast';

export default function InstituteCreate() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', description: '', phone: '', email: '', website: '', address: '', city: '', state: '', pincode: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await client.post('/institutes/create/', form);
      toast.success('Institute created! Awaiting admin approval.');
      navigate('/dashboard/institute');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to create institute');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Create Institute</h1>
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="label">Institute Name *</label><input type="text" name="name" value={form.name} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Description</label><textarea name="description" value={form.description} onChange={handleChange} className="input-field" rows={4} /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Phone</label><input type="tel" name="phone" value={form.phone} onChange={handleChange} className="input-field" /></div>
            <div><label className="label">Email</label><input type="email" name="email" value={form.email} onChange={handleChange} className="input-field" /></div>
          </div>
          <div><label className="label">Website</label><input type="url" name="website" value={form.website} onChange={handleChange} className="input-field" placeholder="https://..." /></div>
          <div><label className="label">Address</label><textarea name="address" value={form.address} onChange={handleChange} className="input-field" rows={2} /></div>
          <div className="grid grid-cols-3 gap-4">
            <div><label className="label">City</label><input type="text" name="city" value={form.city} onChange={handleChange} className="input-field" /></div>
            <div><label className="label">State</label><input type="text" name="state" value={form.state} onChange={handleChange} className="input-field" /></div>
            <div><label className="label">Pincode</label><input type="text" name="pincode" value={form.pincode} onChange={handleChange} className="input-field" /></div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? 'Creating...' : 'Create Institute'}</button>
        </form>
      </div>
    </div>
  );
}
