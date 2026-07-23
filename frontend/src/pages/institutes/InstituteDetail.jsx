import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MapPin, Star, Phone, Mail } from 'lucide-react';
import client from '../../api/client';
import StarRating from '../../components/ui/StarRating';

export default function InstituteDetail() {
  const { id } = useParams();
  const [institute, setInstitute] = useState(null);
  const [branches, setBranches] = useState([]);
  const [courses, setCourses] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('branches');

  useEffect(() => {
    const load = async () => {
      try {
        const [instRes, branchRes, reviewRes] = await Promise.all([
          client.get(`/institutes/${id}/`),
          client.get(`/institutes/${id}/branches/`).catch(() => ({ data: [] })),
          client.get(`/institute-reviews/${id}/`).catch(() => ({ data: [] })),
        ]);
        setInstitute(instRes.data);
        setBranches(Array.isArray(branchRes.data) ? branchRes.data : branchRes.data?.results || []);
        setReviews(Array.isArray(reviewRes.data) ? reviewRes.data : reviewRes.data?.results || []);
      } catch {
        setInstitute(null);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  useEffect(() => {
    if (branches.length > 0) {
      client.get(`/branches/${branches[0].id}/courses/`).then((r) => setCourses(Array.isArray(r.data) ? r.data : r.data?.results || [])).catch(() => {});
    }
  }, [branches]);

  if (loading) return <div className="text-center py-20 text-gray-500">Loading...</div>;
  if (!institute) return <div className="text-center py-20 text-gray-500">Institute not found.</div>;

  const tabs = ['branches', 'courses', 'reviews'];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="card mb-8">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="w-full md:w-64 h-48 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
            {institute.logo ? (
              <img src={institute.logo} alt={institute.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400 text-4xl font-bold">{institute.name?.[0]}</div>
            )}
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold mb-2">{institute.name}</h1>
            <p className="text-gray-500 flex items-center gap-1 mb-2"><MapPin size={16} /> {institute.city || 'India'}{institute.state ? `, ${institute.state}` : ''}</p>
            <div className="flex items-center gap-2 mb-3">
              <StarRating rating={institute.average_rating || 0} readonly size={18} />
              <span className="text-sm text-gray-600">{institute.average_rating || 'N/A'} ({institute.review_count || institute.total_reviews || 0} reviews)</span>
            </div>
            <p className="text-gray-600 mb-4">{institute.description || 'No description available.'}</p>
            {institute.contact_phone && <p className="text-sm text-gray-600 flex items-center gap-1"><Phone size={14} /> {institute.contact_phone}</p>}
            {institute.contact_email && <p className="text-sm text-gray-600 flex items-center gap-1"><Mail size={14} /> {institute.contact_email}</p>}
            <span className={`inline-block mt-3 text-xs px-2 py-1 rounded-full ${institute.is_approved ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
              {institute.is_approved ? 'Verified Institute' : 'Pending Approval'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex gap-1 mb-6 border-b">
        {tabs.map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-2 font-medium text-sm capitalize border-b-2 transition ${activeTab === tab ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'branches' && (
        <div className="space-y-4">
          {branches.length === 0 ? <p className="text-gray-500">No branches available.</p> : branches.map((b) => (
            <div key={b.id} className="card">
              <h3 className="font-semibold">{b.name}</h3>
              <p className="text-sm text-gray-500 flex items-center gap-1 mt-1"><MapPin size={14} /> {b.address || b.city?.name || 'N/A'}</p>
              {b.phone && <p className="text-sm text-gray-500 flex items-center gap-1"><Phone size={14} /> {b.phone}</p>}
            </div>
          ))}
        </div>
      )}

      {activeTab === 'courses' && (
        <div className="space-y-4">
          {courses.length === 0 ? <p className="text-gray-500">No courses available.</p> : courses.map((c) => (
            <Link key={c.id} to={`/courses/${c.id}`} className="card block hover:shadow-md transition">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg hover:text-primary-600">{c.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{c.vehicle_type} - {c.duration_hours || 'N/A'} hours</p>
                  <p className="text-gray-600 text-sm mt-2">{c.description?.slice(0, 150)}...</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-primary-600">₹{c.price}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {activeTab === 'reviews' && (
        <div className="space-y-4">
          {reviews.length === 0 ? <p className="text-gray-500">No reviews yet.</p> : reviews.map((r) => (
            <div key={r.id} className="card">
              <div className="flex items-center gap-2 mb-2">
                <StarRating rating={r.rating} readonly size={16} />
                <span className="text-sm font-medium">{r.student?.name || 'Anonymous'}</span>
                <span className="text-xs text-gray-400">{r.created_at?.split('T')[0]}</span>
              </div>
              <p className="text-gray-600 text-sm">{r.comment}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
