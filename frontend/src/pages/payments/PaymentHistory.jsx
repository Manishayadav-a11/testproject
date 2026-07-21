import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import client from '../../api/client';
import Badge from '../../components/ui/Badge';
import { CreditCard } from 'lucide-react';

export default function PaymentHistory() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get('/my-payments/').then((r) => setPayments(r.data?.results || r.data || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Payment History</h1>
      {loading ? <div className="text-center py-20 text-gray-500">Loading...</div> : payments.length === 0 ? (
        <div className="card text-center py-10">
          <CreditCard size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">No payments yet.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {payments.map((p) => (
            <Link key={p.id} to={`/payments/${p.id}`} className="card block hover:shadow-md transition">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">Payment #{p.id}</h3>
                  <p className="text-sm text-gray-500">{p.payment_method || 'N/A'} &middot; {p.created_at?.split('T')[0]}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold">₹{p.amount}</p>
                  <Badge variant={p.status === 'completed' ? 'success' : p.status === 'refunded' ? 'warning' : 'info'}>{p.status}</Badge>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
