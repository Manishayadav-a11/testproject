import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import client from '../../api/client';
import toast from 'react-hot-toast';
import { CreditCard, Banknote, Smartphone, Building2 } from 'lucide-react';

export default function PaymentCreate() {
  const navigate = useNavigate();
  const location = useLocation();
  const prefill = location.state || {};
  const [form, setForm] = useState({ booking: prefill.bookingId || '', payment_method: 'upi' });
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null);

  useEffect(() => {
    client.get('/bookings/').then((r) => {
      const all = Array.isArray(r.data) ? r.data : r.data?.results || [];
      setBookings(all.filter((b) => b.status === 'pending' || b.status === 'confirmed'));
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (form.booking) {
      const b = bookings.find((b) => String(b.id) === String(form.booking));
      setSelectedBooking(b || null);
    }
  }, [form.booking, bookings]);

  const methods = [
    { value: 'upi', label: 'UPI', icon: <Smartphone size={20} /> },
    { value: 'card', label: 'Credit/Debit Card', icon: <CreditCard size={20} /> },
    { value: 'bank_transfer', label: 'Bank Transfer', icon: <Building2 size={20} /> },
    { value: 'cash', label: 'Cash', icon: <Banknote size={20} /> },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await client.post('/payments/create/', form);
      toast.success('Payment initiated!');
      await client.post(`/payments/${res.data.id}/process/`);
      toast.success('Payment processed!');
      navigate('/payments');
    } catch (err) {
      const data = err.response?.data;
      const msg = typeof data === 'object' ? Object.values(data).flat().join(', ') : 'Payment failed';
      toast.error(msg);
    } finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Make Payment</h1>
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Select Booking *</label>
            <select value={form.booking} onChange={(e) => setForm({ ...form, booking: e.target.value })} className="input-field" required>
              <option value="">Select a booking to pay for</option>
              {bookings.map((b) => <option key={b.id} value={b.id}>Booking #{b.id} - {b.course?.name || 'Course'} (₹{b.final_amount || b.total_amount})</option>)}
            </select>
            {bookings.length === 0 && <p className="text-sm text-gray-500 mt-1">No pending bookings to pay for.</p>}
          </div>

          {selectedBooking && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium mb-2">Payment Summary</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between"><span className="text-gray-500">Course</span><span>{selectedBooking.course?.name}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">Total Amount</span><span>₹{selectedBooking.total_amount}</span></div>
                {selectedBooking.discount_amount > 0 && <div className="flex justify-between"><span className="text-gray-500">Discount</span><span className="text-green-600">-₹{selectedBooking.discount_amount}</span></div>}
                <div className="flex justify-between font-bold border-t pt-1"><span>Final Amount</span><span className="text-primary-600">₹{selectedBooking.final_amount}</span></div>
              </div>
            </div>
          )}

          <div>
            <label className="label">Payment Method *</label>
            <div className="grid grid-cols-2 gap-3">
              {methods.map((m) => (
                <button key={m.value} type="button" onClick={() => setForm({ ...form, payment_method: m.value })} className={`flex items-center gap-2 p-3 rounded-lg border-2 transition ${form.payment_method === m.value ? 'border-primary-600 bg-primary-50' : 'border-gray-200 hover:border-gray-300'}`}>
                  {m.icon}
                  <span className="text-sm font-medium">{m.label}</span>
                </button>
              ))}
            </div>
          </div>

          <button type="submit" disabled={loading || !form.booking} className="btn-primary w-full">{loading ? 'Processing...' : 'Pay Now'}</button>
        </form>
      </div>
    </div>
  );
}
