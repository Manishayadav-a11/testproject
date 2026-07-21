import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Building, BookOpen, Users, Star, Plus } from 'lucide-react';
import client from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import Badge from '../../components/ui/Badge';

export default function InstituteDashboard() {
  const { user } = useAuth();
  const [institutes, setInstitutes] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [instRes, bkRes] = await Promise.all([
          client.get('/institutes/mine/'),
          client.get('/bookings/').catch(() => ({ data: [] })),
        ]);
        setInstitutes(instRes.data?.results || instRes.data || []);
        setBookings(bkRes.data?.results || bkRes.data || []);
      } catch {} finally { setLoading(false); }
    };
    load();
  }, []);

  if (loading) return <div className="text-center py-20 text-gray-500">Loading dashboard...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Institute Dashboard</h1>
        <Link to="/institutes/create" className="btn-primary flex items-center gap-2"><Plus size={18} /> New Institute</Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-primary-100 rounded-lg"><Building className="text-primary-600" size={24} /></div>
          <div><p className="text-sm text-gray-500">Institutes</p><p className="text-2xl font-bold">{institutes.length}</p></div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-green-100 rounded-lg"><BookOpen className="text-green-600" size={24} /></div>
          <div><p className="text-sm text-gray-500">Total Bookings</p><p className="text-2xl font-bold">{bookings.length}</p></div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-yellow-100 rounded-lg"><Star className="text-yellow-600" size={24} /></div>
          <div><p className="text-sm text-gray-500">Avg Rating</p><p className="text-2xl font-bold">-</p></div>
        </div>
      </div>

      <h2 className="text-lg font-semibold mb-4">My Institutes</h2>
      {institutes.length === 0 ? (
        <div className="card text-center py-10">
          <p className="text-gray-500 mb-4">You haven't created any institutes yet.</p>
          <Link to="/institutes/create" className="btn-primary">Create Your First Institute</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {institutes.map((inst) => (
            <div key={inst.id} className="card flex items-center justify-between">
              <div>
                <h3 className="font-semibold">{inst.name}</h3>
                <p className="text-sm text-gray-500">{inst.city || 'India'}</p>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={inst.is_approved ? 'success' : 'warning'}>{inst.is_approved ? 'Approved' : 'Pending'}</Badge>
                <Link to={`/institutes/${inst.id}`} className="text-primary-600 text-sm hover:underline">View</Link>
              </div>
            </div>
          ))}
        </div>
      )}

      <h2 className="text-lg font-semibold mt-8 mb-4">Recent Bookings</h2>
      {bookings.length === 0 ? (
        <div className="card text-center py-10"><p className="text-gray-500">No bookings yet.</p></div>
      ) : (
        <div className="space-y-3">
          {bookings.slice(0, 10).map((b) => (
            <div key={b.id} className="card flex items-center justify-between">
              <div>
                <p className="font-medium">{b.course?.name || `Booking #${b.id}`}</p>
                <p className="text-sm text-gray-500">{b.created_at?.split('T')[0]}</p>
              </div>
              <Badge variant={b.status === 'confirmed' ? 'success' : b.status === 'cancelled' ? 'danger' : 'warning'}>{b.status}</Badge>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
