import { useState, useEffect } from 'react';
import { Users, Building, BookOpen, CreditCard } from 'lucide-react';
import client from '../../api/client';
import Badge from '../../components/ui/Badge';
import { useAuth } from '../../context/AuthContext';

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ users: 0, institutes: 0, bookings: 0, payments: 0 });
  const [users, setUsers] = useState([]);
  const [institutes, setInstitutes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [uRes, iRes, bRes, pRes] = await Promise.all([
          client.get('/auth/users/').catch(() => ({ data: [] })),
          client.get('/institutes/').catch(() => ({ data: [] })),
          client.get('/bookings/').catch(() => ({ data: [] })),
          client.get('/payments/').catch(() => ({ data: [] })),
        ]);
        const uData = uRes.data?.results || uRes.data || [];
        const iData = iRes.data?.results || iRes.data || [];
        const bData = bRes.data?.results || bRes.data || [];
        const pData = pRes.data?.results || pRes.data || [];
        setUsers(uData);
        setInstitutes(iData);
        setStats({ users: uData.length, institutes: iData.length, bookings: bData.length, payments: pData.length });
      } catch {} finally { setLoading(false); }
    };
    load();
  }, []);

  const handleApprove = async (id) => {
    try {
      await client.post(`/institutes/${id}/approve/`);
      setInstitutes(institutes.map((i) => i.id === id ? { ...i, is_approved: true } : i));
    } catch {}
  };

  if (loading) return <div className="text-center py-20 text-gray-500">Loading admin dashboard...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-2xl font-bold mb-8">Admin Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {[
          { icon: <Users className="text-blue-600" size={24} />, label: 'Users', value: stats.users, bg: 'bg-blue-100' },
          { icon: <Building className="text-primary-600" size={24} />, label: 'Institutes', value: stats.institutes, bg: 'bg-primary-100' },
          { icon: <BookOpen className="text-green-600" size={24} />, label: 'Bookings', value: stats.bookings, bg: 'bg-green-100' },
          { icon: <CreditCard className="text-yellow-600" size={24} />, label: 'Payments', value: stats.payments, bg: 'bg-yellow-100' },
        ].map((s, i) => (
          <div key={i} className="card flex items-center gap-4">
            <div className={`p-3 ${s.bg} rounded-lg`}>{s.icon}</div>
            <div><p className="text-sm text-gray-500">{s.label}</p><p className="text-2xl font-bold">{s.value}</p></div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-lg font-semibold mb-4">Institutes (Pending Approval)</h2>
          {institutes.filter((i) => !i.is_approved).length === 0 ? (
            <div className="card text-center py-6"><p className="text-gray-500">No pending institutes.</p></div>
          ) : (
            <div className="space-y-3">
              {institutes.filter((i) => !i.is_approved).map((inst) => (
                <div key={inst.id} className="card flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">{inst.name}</h3>
                    <p className="text-sm text-gray-500">{inst.city || 'India'}</p>
                  </div>
                  <button onClick={() => handleApprove(inst.id)} className="btn-success text-sm">Approve</button>
                </div>
              ))}
            </div>
          )}
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-4">All Users</h2>
          <div className="card">
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {users.map((u) => (
                <div key={u.id} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div>
                    <p className="font-medium text-sm">{u.first_name} {u.last_name}</p>
                    <p className="text-xs text-gray-500">{u.email}</p>
                  </div>
                  <Badge variant={u.role === 'admin' ? 'danger' : u.role === 'institute_owner' ? 'info' : u.role === 'instructor' ? 'warning' : 'neutral'}>{u.role}</Badge>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
