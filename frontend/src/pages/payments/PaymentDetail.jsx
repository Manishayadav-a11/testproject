import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import client from '../../api/client';
import Badge from '../../components/ui/Badge';

export default function PaymentDetail() {
  const { id } = useParams();
  const [payment, setPayment] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get(`/payments/${id}/`).then((r) => setPayment(r.data)).catch(() => setPayment(null)).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-center py-20 text-gray-500">Loading...</div>;
  if (!payment) return <div className="text-center py-20 text-gray-500">Payment not found.</div>;

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Payment #{payment.id}</h1>
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <span className="text-3xl font-bold text-primary-600">₹{payment.amount}</span>
          <Badge variant={payment.status === 'completed' ? 'success' : payment.status === 'refunded' ? 'warning' : 'info'}>{payment.status}</Badge>
        </div>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between"><span className="text-gray-500">Payment ID</span><span className="font-medium">{payment.id}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Method</span><span className="font-medium">{payment.payment_method || 'N/A'}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Transaction ID</span><span className="font-medium">{payment.transaction_id || 'N/A'}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Booking</span><span className="font-medium">#{payment.booking?.id || 'N/A'}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Date</span><span className="font-medium">{payment.created_at?.split('T')[0]}</span></div>
          {payment.platform_commission && <div className="flex justify-between"><span className="text-gray-500">Platform Commission</span><span className="font-medium">₹{payment.platform_commission}</span></div>}
        </div>
      </div>
    </div>
  );
}
