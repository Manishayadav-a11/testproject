import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import StarRating from '../../components/ui/StarRating';
import toast from 'react-hot-toast';

export default function ReviewCreate() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ rating: 0, title: '', comment: '', course: '', institute: '' });
  const [courses, setCourses] = useState([]);
  const [institutes, setInstitutes] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    client.get('/courses/').then((r) => setCourses(r.data?.results || r.data || [])).catch(() => {});
    client.get('/institutes/').then((r) => setInstitutes(r.data?.results || r.data || [])).catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.rating === 0) { toast.error('Please select a rating'); return; }
    setLoading(true);
    try {
      await client.post('/reviews/create/', form);
      toast.success('Review submitted!');
      navigate('/reviews');
    } catch (err) { toast.error(err.response?.data?.error || 'Failed to submit review'); } finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Write a Review</h1>
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Rating *</label>
            <StarRating rating={form.rating} onChange={(r) => setForm({ ...form, rating: r })} size={28} />
          </div>
          <div>
            <label className="label">Title</label>
            <input type="text" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="input-field" placeholder="Sum up your experience" />
          </div>
          <div>
            <label className="label">Review *</label>
            <textarea value={form.comment} onChange={(e) => setForm({ ...form, comment: e.target.value })} className="input-field" rows={4} required placeholder="Share your experience..." />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Course (optional)</label>
              <select value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })} className="input-field">
                <option value="">Select course</option>
                {courses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Institute (optional)</label>
              <select value={form.institute} onChange={(e) => setForm({ ...form, institute: e.target.value })} className="input-field">
                <option value="">Select institute</option>
                {institutes.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}
              </select>
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? 'Submitting...' : 'Submit Review'}</button>
        </form>
      </div>
    </div>
  );
}
