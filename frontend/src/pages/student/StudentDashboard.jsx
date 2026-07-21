import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, CreditCard, Star, Calendar } from 'lucide-react';
import client from '../../api/client';
import Badge from '../../components/ui/Badge';

export default function StudentDashboard() {
  const [bookings, setBookings] = useState([]);
  const [payments, setPayments] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [bk, pm, rv] = await Promise.all([
          client.get('/bookings/').catch(() => ({ data: [] })),
          client.get('/my-payments/').catch(() => ({ data: [] })),
          client.get('/reviews/').catch(() => ({ data: [] })),
        ]);
        setBookings(bk.data?.results || bk.data || []);
        setPayments(pm.data?.results || pm.data || []);
        setReviews(rv.data?.results || rv.data || []);
      } catch {} finally { setLoading(false); }
    };
    load();
  }, []);

  if (loading) return <div className="text-center py-20 text-gray-500">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-2xl font-bold mb-8">Student Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-primary-100 rounded-lg"><Calendar className="text-primary-600" size={24} /></div>
          <div><p className="text-sm text-gray-500">Bookings</p><p className="text-2xl font-bold">{bookings.length}</p></div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-green-100 rounded-lg"><CreditCard className="text-green-600" size={24} /></div>
          <div><p className="text-sm text-gray-500">Payments</p><p className="text-2xl font-bold">{payments.length}</p></div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-yellow-100 rounded-lg"><Star className="text-yellow-600" size={24} /></div>
          <div><p className="text-sm text-gray-500">Reviews</p><p className="text-2xl font-bold">{reviews.length}</p></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Bookings</h2>
            <Link to="/bookings" className="text-primary-600 text-sm hover:underline">View All</Link>
          </div>
          {bookings.length === 0 ? (
            <div className="card text-center py-6"><p className="text-gray-500">No bookings yet.</p><Link to="/courses" className="text-primary-600 text-sm hover:underline mt-2 inline-block">Browse Courses</Link></div>
          ) : (
            <div className="space-y-3">
              {bookings.slice(0, 5).map((b) => (
                <Link key={b.id} to={`/bookings/${b.id}`} className="card block hover:shadow-md transition">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{b.course?.name || `Booking #${b.id}`}</span>
                    <Badge variant={b.status === 'confirmed' ? 'success' : b.status === 'cancelled' ? 'danger' : 'warning'}>{b.status}</Badge>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Payments</h2>
            <Link to="/payments" className="text-primary-600 text-sm hover:underline">View All</Link>
          </div>
          {payments.length === 0 ? (
            <div className="card text-center py-6"><p className="text-gray-500">No payments yet.</p></div>
          ) : (
            <div className="space-y-3">
              {payments.slice(0, 5).map((p) => (
                <Link key={p.id} to={`/payments/${p.id}`} className="card block hover:shadow-md transition">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">₹{p.amount}</span>
                    <Badge variant={p.status === 'completed' ? 'success' : 'info'}>{p.status}</Badge>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
