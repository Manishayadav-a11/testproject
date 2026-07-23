import { useState, useEffect } from 'react';
import client from '../../api/client';
import Badge from '../../components/ui/Badge';
import { MapPin, Plus, Phone } from 'lucide-react';
import Modal from '../../components/ui/Modal';
import toast from 'react-hot-toast';

export default function BranchList() {
  const [branches, setBranches] = useState([]);
  const [institutes, setInstitutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: '', institute: '', address: '', city: '', state: '', pincode: '', phone: '', email: '' });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    client.get('/branches/').then((r) => setBranches(Array.isArray(r.data) ? r.data : r.data?.results || [])).catch(() => {}).finally(() => setLoading(false));
    client.get('/institutes/mine/').then((r) => setInstitutes(Array.isArray(r.data) ? r.data : r.data?.results || [])).catch(() => {});
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await client.post('/branches/', form);
      toast.success('Branch created!');
      setShowCreate(false);
      setForm({ name: '', institute: '', address: '', city: '', state: '', pincode: '', phone: '', email: '' });
      const r = await client.get('/branches/');
      setBranches(Array.isArray(r.data) ? r.data : r.data?.results || []);
    } catch (err) {
      const data = err.response?.data;
      toast.error(typeof data === 'object' ? Object.values(data).flat().join(', ') : 'Failed');
    } finally { setSubmitting(false); }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this branch?')) return;
    try {
      await client.delete(`/branches/${id}/delete/`);
      setBranches(branches.filter((b) => b.id !== id));
      toast.success('Deleted');
    } catch { toast.error('Failed to delete'); }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Branches</h1>
        <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2"><Plus size={18} /> Add Branch</button>
      </div>

      {loading ? <div className="text-center py-20 text-gray-500">Loading...</div> : branches.length === 0 ? (
        <div className="card text-center py-10">
          <MapPin size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">No branches yet.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {branches.map((b) => (
            <div key={b.id} className="card flex items-center justify-between">
              <div>
                <h3 className="font-semibold">{b.name}</h3>
                <p className="text-sm text-gray-500 flex items-center gap-1"><MapPin size={14} /> {b.address || b.city?.name || 'N/A'}</p>
                {b.phone && <p className="text-xs text-gray-400 flex items-center gap-1"><Phone size={12} /> {b.phone}</p>}
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={b.is_active !== false ? 'success' : 'danger'}>{b.is_active !== false ? 'Active' : 'Inactive'}</Badge>
                <button onClick={() => handleDelete(b.id)} className="text-red-500 text-sm hover:underline">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Add Branch">
        <form onSubmit={handleCreate} className="space-y-4">
          <div><label className="label">Branch Name *</label><input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="input-field" required /></div>
          {institutes.length > 0 && (
            <div><label className="label">Institute *</label><select value={form.institute} onChange={(e) => setForm({ ...form, institute: e.target.value })} className="input-field" required><option value="">Select institute</option>{institutes.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}</select></div>
          )}
          <div><label className="label">Address</label><textarea value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} className="input-field" rows={2} /></div>
          <div className="grid grid-cols-3 gap-4">
            <div><label className="label">City</label><input type="text" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} className="input-field" /></div>
            <div><label className="label">State</label><input type="text" value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} className="input-field" /></div>
            <div><label className="label">Pincode</label><input type="text" value={form.pincode} onChange={(e) => setForm({ ...form, pincode: e.target.value })} className="input-field" /></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Phone</label><input type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="input-field" /></div>
            <div><label className="label">Email</label><input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="input-field" /></div>
          </div>
          <button type="submit" disabled={submitting} className="btn-primary w-full">{submitting ? 'Creating...' : 'Create Branch'}</button>
        </form>
      </Modal>
    </div>
  );
}
