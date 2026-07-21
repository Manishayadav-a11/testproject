import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import client from '../../api/client';
import toast from 'react-hot-toast';

export default function BookingCreate() {
  const navigate = useNavigate();
  const location = useLocation();
  const prefill = location.state || {};
  const [form, setForm] = useState({ course: prefill.courseId || '', preferred_date: '', preferred_time: '', notes: '' });
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    client.get('/courses/').then((r) => setCourses(r.data?.results || r.data || [])).catch(() => {});
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post('/bookings/create/', form);
      toast.success('Booking created!');
      navigate('/bookings');
    } catch (err) {
      toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to create booking');
    } finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Create Booking</h1>
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Course *</label>
            <select name="course" value={form.course} onChange={handleChange} className="input-field" required>
              <option value="">Select a course</option>
              {courses.map((c) => <option key={c.id} value={c.id}>{c.name} - ₹{c.price} ({c.institute?.name})</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Preferred Date *</label><input type="date" name="preferred_date" value={form.preferred_date} onChange={handleChange} className="input-field" required /></div>
            <div><label className="label">Preferred Time</label><input type="time" name="preferred_time" value={form.preferred_time} onChange={handleChange} className="input-field" /></div>
          </div>
          <div><label className="label">Notes</label><textarea name="notes" value={form.notes} onChange={handleChange} className="input-field" rows={3} placeholder="Any special requests..." /></div>
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? 'Creating...' : 'Create Booking'}</button>
        </form>
      </div>
    </div>
  );
}
