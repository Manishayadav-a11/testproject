import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import client from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import Badge from '../../components/ui/Badge';
import toast from 'react-hot-toast';

export default function BookingDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get(`/bookings/${id}/`).then((r) => setBooking(r.data)).catch(() => setBooking(null)).finally(() => setLoading(false));
  }, [id]);

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel this booking?')) return;
    try {
      await client.post(`/bookings/${id}/cancel/`);
      toast.success('Booking cancelled');
      setBooking({ ...booking, status: 'cancelled' });
    } catch (err) { toast.error(err.response?.data?.error || 'Failed to cancel'); }
  };

  const handleConfirm = async () => {
    try {
      await client.post(`/bookings/${id}/confirm/`);
      toast.success('Booking confirmed');
      setBooking({ ...booking, status: 'confirmed' });
    } catch (err) { toast.error(err.response?.data?.error || 'Failed'); }
  };

  if (loading) return <div className="text-center py-20 text-gray-500">Loading...</div>;
  if (!booking) return <div className="text-center py-20 text-gray-500">Booking not found.</div>;

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Booking #{booking.id}</h1>
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <Badge variant={booking.status === 'confirmed' ? 'success' : booking.status === 'cancelled' ? 'danger' : 'warning'}>{booking.status}</Badge>
        </div>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between"><span className="text-gray-500">Course</span><span className="font-medium">{booking.course?.name || 'N/A'}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Institute</span><span className="font-medium">{booking.institute?.name || 'N/A'}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Date</span><span className="font-medium">{booking.preferred_date || 'Not set'}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Time</span><span className="font-medium">{booking.preferred_time || 'Not set'}</span></div>
          {booking.total_amount && <div className="flex justify-between"><span className="text-gray-500">Amount</span><span className="font-bold text-primary-600">₹{booking.total_amount}</span></div>}
          <div className="flex justify-between"><span className="text-gray-500">Created</span><span className="font-medium">{booking.created_at?.split('T')[0]}</span></div>
          {booking.notes && <div><span className="text-gray-500">Notes:</span><p className="mt-1">{booking.notes}</p></div>}
        </div>
        <div className="flex gap-3 mt-6 pt-4 border-t">
          {booking.status === 'pending' && user?.role === 'institute_owner' && (
            <button onClick={handleConfirm} className="btn-success">Confirm</button>
          )}
          {(booking.status === 'pending' || booking.status === 'confirmed') && (
            <button onClick={handleCancel} className="btn-danger">Cancel Booking</button>
          )}
          {booking.status === 'confirmed' && user?.role === 'student' && (
            <button onClick={() => navigate('/payments/create', { state: { bookingId: booking.id, amount: booking.total_amount } })} className="btn-primary">Pay Now</button>
          )}
        </div>
      </div>
    </div>
  );
}
