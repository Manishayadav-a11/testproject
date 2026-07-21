import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Clock, IndianRupee } from 'lucide-react';
import client from '../../api/client';
import Pagination from '../../components/ui/Pagination';

export default function CourseList() {
  const [courses, setCourses] = useState([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  const fetchCourses = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      params.append('page', page);
      const res = await client.get(`/courses/?${params.toString()}`);
      setCourses(res.data?.results || res.data || []);
      setTotalPages(res.data?.total_pages || Math.ceil((res.data?.count || 0) / 12) || 1);
    } catch { setCourses([]); } finally { setLoading(false); }
  };

  useEffect(() => { fetchCourses(); }, [page, search]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <h1 className="text-2xl font-bold">Courses</h1>
        <div className="relative">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input type="text" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className="input-field pl-10 w-72" placeholder="Search courses..." />
        </div>
      </div>
      {loading ? (
        <div className="text-center py-20 text-gray-500">Loading...</div>
      ) : courses.length === 0 ? (
        <div className="text-center py-20 text-gray-500">No courses found.</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((c) => (
              <Link key={c.id} to={`/courses/${c.id}`} className="card hover:shadow-md transition group">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs px-2 py-1 bg-primary-100 text-primary-700 rounded-full">{c.vehicle_type}</span>
                  <span className="text-lg font-bold text-primary-600">₹{c.price}</span>
                </div>
                <h3 className="font-semibold text-lg group-hover:text-primary-600 transition mb-1">{c.name}</h3>
                <p className="text-sm text-gray-500 mb-2">{c.institute?.name || 'Unknown Institute'}</p>
                <p className="text-gray-600 text-sm line-clamp-2">{c.description || 'No description.'}</p>
                <div className="flex items-center gap-4 mt-4 pt-3 border-t text-sm text-gray-500">
                  {c.duration_hours && <span className="flex items-center gap-1"><Clock size={14} /> {c.duration_hours}h</span>}
                  {c.lessons_count && <span>{c.lessons_count} lessons</span>}
                </div>
              </Link>
            ))}
          </div>
          <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
