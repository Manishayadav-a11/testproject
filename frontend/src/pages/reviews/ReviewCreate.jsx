import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import StarRating from '../../components/ui/StarRating';
import toast from 'react-hot-toast';

export default function ReviewCreate() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ booking: '', rating: 0, comment: '', institute_rating: 0, instructor_rating: 0, course_rating: 0 });
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    client.get('/bookings/').then((r) => {
      const all = Array.isArray(r.data) ? r.data : r.data?.results || [];
      setBookings(all.filter((b) => b.status === 'completed'));
    }).catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.rating === 0) { toast.error('Please select a rating'); return; }
    if (!form.booking) { toast.error('Please select a booking'); return; }
    setLoading(true);
    try {
      await client.post('/reviews/create/', form);
      toast.success('Review submitted!');
      navigate('/reviews');
    } catch (err) {
      const data = err.response?.data;
      const msg = typeof data === 'object' ? Object.values(data).flat().join(', ') : 'Failed to submit review';
      toast.error(msg);
    } finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Write a Review</h1>
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Completed Booking *</label>
            <select value={form.booking} onChange={(e) => setForm({ ...form, booking: e.target.value })} className="input-field" required>
              <option value="">Select a completed booking</option>
              {bookings.map((b) => <option key={b.id} value={b.id}>Booking #{b.id} - {b.course?.name || 'Course'}</option>)}
            </select>
            {bookings.length === 0 && <p className="text-sm text-gray-500 mt-1">No completed bookings available for review.</p>}
          </div>
          <div>
            <label className="label">Overall Rating *</label>
            <StarRating rating={form.rating} onChange={(r) => setForm({ ...form, rating: r })} size={28} />
          </div>
          <div>
            <label className="label">Review *</label>
            <textarea value={form.comment} onChange={(e) => setForm({ ...form, comment: e.target.value })} className="input-field" rows={4} required placeholder="Share your experience..." />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">Institute Rating</label>
              <StarRating rating={form.institute_rating} onChange={(r) => setForm({ ...form, institute_rating: r })} size={20} />
            </div>
            <div>
              <label className="label">Instructor Rating</label>
              <StarRating rating={form.instructor_rating} onChange={(r) => setForm({ ...form, instructor_rating: r })} size={20} />
            </div>
            <div>
              <label className="label">Course Rating</label>
              <StarRating rating={form.course_rating} onChange={(r) => setForm({ ...form, course_rating: r })} size={20} />
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? 'Submitting...' : 'Submit Review'}</button>
        </form>
      </div>
    </div>
  );
}
