import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import client from '../../api/client';
import StarRating from '../../components/ui/StarRating';
import { Star } from 'lucide-react';

export default function ReviewList() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get('/reviews/').then((r) => setReviews(r.data?.results || r.data || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Reviews</h1>
        <Link to="/reviews/create" className="btn-primary flex items-center gap-2"><Star size={18} /> Write Review</Link>
      </div>
      {loading ? <div className="text-center py-20 text-gray-500">Loading...</div> : reviews.length === 0 ? (
        <div className="card text-center py-10">
          <Star size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">No reviews yet. Be the first to write one!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map((r) => (
            <div key={r.id} className="card">
              <div className="flex items-center gap-3 mb-2">
                <StarRating rating={r.rating} readonly size={16} />
                <span className="font-medium text-sm">{r.user?.first_name || 'Anonymous'}</span>
                <span className="text-xs text-gray-400">{r.created_at?.split('T')[0]}</span>
              </div>
              {r.title && <h3 className="font-medium mb-1">{r.title}</h3>}
              <p className="text-gray-600 text-sm">{r.comment}</p>
              {r.institute && <p className="text-xs text-gray-400 mt-2">Institute: {r.institute.name}</p>}
              {r.course && <p className="text-xs text-gray-400">Course: {r.course.name}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
