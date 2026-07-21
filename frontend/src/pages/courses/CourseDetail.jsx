import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Clock, IndianRupee, MapPin, Star, BookOpen } from 'lucide-react';
import client from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import StarRating from '../../components/ui/StarRating';
import toast from 'react-hot-toast';

export default function CourseDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [cRes, rRes] = await Promise.all([
          client.get(`/courses/${id}/`),
          client.get(`/course-reviews/${id}/`).catch(() => ({ data: [] })),
        ]);
        setCourse(cRes.data);
        setReviews(rRes.data?.results || rRes.data || []);
      } catch { setCourse(null); } finally { setLoading(false); }
    };
    load();
  }, [id]);

  const handleBookNow = () => {
    if (!user) { toast.error('Please login to book'); navigate('/login'); return; }
    navigate('/bookings/create', { state: { courseId: course.id, courseName: course.name } });
  };

  if (loading) return <div className="text-center py-20 text-gray-500">Loading...</div>;
  if (!course) return <div className="text-center py-20 text-gray-500">Course not found.</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="card mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <span className="text-xs px-2 py-1 bg-primary-100 text-primary-700 rounded-full">{course.vehicle_type}</span>
            <h1 className="text-2xl font-bold mt-2">{course.name}</h1>
            <p className="text-gray-500 mt-1">{course.institute?.name || 'Unknown Institute'}</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-primary-600">₹{course.price}</p>
          </div>
        </div>
        <p className="text-gray-600 mb-6">{course.description}</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {course.duration_hours && <div className="bg-gray-50 p-3 rounded-lg text-center"><Clock size={20} className="mx-auto text-gray-400 mb-1" /><p className="text-sm font-medium">{course.duration_hours} hours</p></div>}
          {course.lessons_count && <div className="bg-gray-50 p-3 rounded-lg text-center"><BookOpen size={20} className="mx-auto text-gray-400 mb-1" /><p className="text-sm font-medium">{course.lessons_count} lessons</p></div>}
        </div>
        {user?.role === 'student' && (
          <button onClick={handleBookNow} className="btn-primary w-full text-center">Book This Course</button>
        )}
      </div>

      <h2 className="text-lg font-semibold mb-4">Reviews ({reviews.length})</h2>
      {reviews.length === 0 ? <p className="text-gray-500">No reviews yet.</p> : (
        <div className="space-y-4">
          {reviews.map((r) => (
            <div key={r.id} className="card">
              <div className="flex items-center gap-2 mb-2">
                <StarRating rating={r.rating} readonly size={16} />
                <span className="text-sm font-medium">{r.user?.first_name || 'Anonymous'}</span>
              </div>
              <p className="text-gray-600 text-sm">{r.comment}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
