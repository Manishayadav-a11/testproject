import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import toast from 'react-hot-toast';

export default function CourseCreate() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', description: '', vehicle_type: 'LMV', price: '', duration_hours: '', lessons_count: '', branch: '' });
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    client.get('/institutes/mine/').then((r) => {
      const insts = r.data?.results || r.data || [];
      if (insts.length > 0) {
        client.get(`/institutes/${insts[0].id}/branches/`).then((br) => setBranches(br.data?.results || br.data || [])).catch(() => {});
      }
    }).catch(() => {});
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post('/courses/', { ...form, price: parseFloat(form.price), duration_hours: parseInt(form.duration_hours) || undefined, lessons_count: parseInt(form.lessons_count) || undefined });
      toast.success('Course created!');
      navigate('/dashboard/institute');
    } catch (err) { toast.error(err.response?.data?.error || 'Failed'); } finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Create Course</h1>
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="label">Course Name *</label><input type="text" name="name" value={form.name} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Description</label><textarea name="description" value={form.description} onChange={handleChange} className="input-field" rows={3} /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Vehicle Type</label><select name="vehicle_type" value={form.vehicle_type} onChange={handleChange} className="input-field"><option>LMV</option><option>HMV</option><option>MCWG</option><option>MCWOG</option><option>HGMV</option><option>HPMV</option></select></div>
            <div><label className="label">Price (₹) *</label><input type="number" name="price" value={form.price} onChange={handleChange} className="input-field" required min="0" /></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Duration (hours)</label><input type="number" name="duration_hours" value={form.duration_hours} onChange={handleChange} className="input-field" min="0" /></div>
            <div><label className="label">Lessons Count</label><input type="number" name="lessons_count" value={form.lessons_count} onChange={handleChange} className="input-field" min="0" /></div>
          </div>
          {branches.length > 0 && (
            <div><label className="label">Branch</label><select name="branch" value={form.branch} onChange={handleChange} className="input-field"><option value="">Select branch</option>{branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}</select></div>
          )}
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? 'Creating...' : 'Create Course'}</button>
        </form>
      </div>
    </div>
  );
}
