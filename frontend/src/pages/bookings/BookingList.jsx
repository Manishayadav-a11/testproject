import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import client from '../../api/client';
import Badge from '../../components/ui/Badge';
import { Calendar } from 'lucide-react';

export default function BookingList() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get('/bookings/').then((r) => setBookings(r.data?.results || r.data || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">My Bookings</h1>
        <Link to="/bookings/create" className="btn-primary">New Booking</Link>
      </div>
      {loading ? <div className="text-center py-20 text-gray-500">Loading...</div> : bookings.length === 0 ? (
        <div className="card text-center py-10">
          <Calendar size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 mb-4">No bookings yet.</p>
          <Link to="/courses" className="btn-primary">Browse Courses</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((b) => (
            <Link key={b.id} to={`/bookings/${b.id}`} className="card block hover:shadow-md transition">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">{b.course?.name || `Booking #${b.id}`}</h3>
                  <p className="text-sm text-gray-500 mt-1">Institute: {b.institute?.name || 'N/A'}</p>
                  <p className="text-sm text-gray-500">{b.preferred_date || b.created_at?.split('T')[0]}</p>
                </div>
                <div className="text-right">
                  <Badge variant={b.status === 'confirmed' ? 'success' : b.status === 'cancelled' ? 'danger' : b.status === 'completed' ? 'info' : 'warning'}>{b.status}</Badge>
                  {b.total_amount && <p className="text-lg font-bold text-primary-600 mt-2">₹{b.total_amount}</p>}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
