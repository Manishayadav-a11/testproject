import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import client from '../../api/client';
import toast from 'react-hot-toast';

export default function BookingCreate() {
  const navigate = useNavigate();
  const location = useLocation();
  const prefill = location.state || {};
  const [form, setForm] = useState({
    course: prefill.courseId || '',
    branch: '',
    booking_date: '',
    preferred_time_slot: '',
    instructor: '',
    special_requests: '',
  });
  const [courses, setCourses] = useState([]);
  const [branches, setBranches] = useState([]);
  const [instructors, setInstructors] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    client.get('/courses/').then((r) => setCourses(Array.isArray(r.data) ? r.data : r.data?.results || [])).catch(() => {});
    client.get('/branches/').then((r) => setBranches(Array.isArray(r.data) ? r.data : r.data?.results || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (form.branch) {
      client.get(`/branches/${form.branch}/instructors/`).then((r) => setInstructors(Array.isArray(r.data) ? r.data : r.data?.results || [])).catch(() => {});
    }
  }, [form.branch]);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post('/bookings/create/', form);
      toast.success('Booking created!');
      navigate('/bookings');
    } catch (err) {
      const data = err.response?.data;
      const msg = typeof data === 'object' ? Object.values(data).flat().join(', ') : 'Failed to create booking';
      toast.error(msg);
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
              {courses.map((c) => <option key={c.id} value={c.id}>{c.name} - ₹{c.price}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Branch *</label>
            <select name="branch" value={form.branch} onChange={handleChange} className="input-field" required>
              <option value="">Select a branch</option>
              {branches.map((b) => <option key={b.id} value={b.id}>{b.name} - {b.city?.name || b.address || ''}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Booking Date *</label><input type="date" name="booking_date" value={form.booking_date} onChange={handleChange} className="input-field" required min={new Date().toISOString().split('T')[0]} /></div>
            <div><label className="label">Preferred Time Slot</label><input type="time" name="preferred_time_slot" value={form.preferred_time_slot} onChange={handleChange} className="input-field" /></div>
          </div>
          {instructors.length > 0 && (
            <div>
              <label className="label">Preferred Instructor</label>
              <select name="instructor" value={form.instructor} onChange={handleChange} className="input-field">
                <option value="">No preference</option>
                {instructors.map((i) => <option key={i.id} value={i.id}>{i.user?.first_name} {i.user?.last_name}</option>)}
              </select>
            </div>
          )}
          <div><label className="label">Special Requests</label><textarea name="special_requests" value={form.special_requests} onChange={handleChange} className="input-field" rows={3} placeholder="Any special requests..." /></div>
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? 'Creating...' : 'Create Booking'}</button>
        </form>
      </div>
    </div>
  );
}
