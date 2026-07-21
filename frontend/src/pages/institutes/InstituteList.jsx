import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, MapPin, Star, Filter } from 'lucide-react';
import client from '../../api/client';
import Pagination from '../../components/ui/Pagination';

export default function InstituteList() {
  const [institutes, setInstitutes] = useState([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [cityFilter, setCityFilter] = useState('');

  const fetchInstitutes = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (cityFilter) params.append('city', cityFilter);
      params.append('page', page);
      const res = await client.get(`/institutes/?${params.toString()}`);
      const data = res.data;
      setInstitutes(data.results || data || []);
      setTotalPages(data.total_pages || Math.ceil((data.count || 0) / 12) || 1);
    } catch {
      setInstitutes([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchInstitutes(); }, [page, search, cityFilter]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <h1 className="text-2xl font-bold">Driving Institutes</h1>
        <div className="flex gap-3">
          <div className="relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input type="text" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className="input-field pl-10 w-64" placeholder="Search institutes..." />
          </div>
          <div className="relative">
            <MapPin size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input type="text" value={cityFilter} onChange={(e) => { setCityFilter(e.target.value); setPage(1); }} className="input-field pl-10 w-48" placeholder="City..." />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-500">Loading...</div>
      ) : institutes.length === 0 ? (
        <div className="text-center py-20 text-gray-500">No institutes found.</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {institutes.map((inst) => (
              <Link key={inst.id} to={`/institutes/${inst.id}`} className="card hover:shadow-md transition group">
                <div className="h-40 bg-gray-100 rounded-lg mb-4 overflow-hidden">
                  {inst.logo ? (
                    <img src={inst.logo} alt={inst.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400 text-3xl font-bold">{inst.name?.[0]}</div>
                  )}
                </div>
                <h3 className="font-semibold text-lg group-hover:text-primary-600 transition">{inst.name}</h3>
                <p className="text-gray-500 text-sm flex items-center gap-1 mt-1"><MapPin size={14} /> {inst.city || 'India'}</p>
                <p className="text-gray-600 text-sm mt-2 line-clamp-2">{inst.description || 'No description available.'}</p>
                <div className="flex items-center justify-between mt-4 pt-3 border-t">
                  <div className="flex items-center gap-1 text-sm">
                    <Star size={14} className="fill-yellow-400 text-yellow-400" />
                    <span>{inst.average_rating || 'N/A'}</span>
                    <span className="text-gray-400">({inst.review_count || 0})</span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${inst.is_approved ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                    {inst.is_approved ? 'Verified' : 'Pending'}
                  </span>
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
