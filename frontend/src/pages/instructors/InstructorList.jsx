import { useState, useEffect } from 'react';
import client from '../../api/client';
import Badge from '../../components/ui/Badge';
import { Users, Plus } from 'lucide-react';
import Modal from '../../components/ui/Modal';
import toast from 'react-hot-toast';

export default function InstructorList() {
  const [instructors, setInstructors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '', license_number: '', experience_years: '', branch: '' });
  const [branches, setBranches] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    client.get('/instructors/').then((r) => setInstructors(Array.isArray(r.data) ? r.data : r.data?.results || [])).catch(() => {}).finally(() => setLoading(false));
    client.get('/branches/').then((r) => setBranches(Array.isArray(r.data) ? r.data : r.data?.results || [])).catch(() => {});
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await client.post('/instructors/create/', form);
      toast.success('Instructor created!');
      setShowCreate(false);
      setForm({ first_name: '', last_name: '', email: '', phone: '', license_number: '', experience_years: '', branch: '' });
      const r = await client.get('/instructors/');
      setInstructors(Array.isArray(r.data) ? r.data : r.data?.results || []);
    } catch (err) {
      const data = err.response?.data;
      toast.error(typeof data === 'object' ? Object.values(data).flat().join(', ') : 'Failed');
    } finally { setSubmitting(false); }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this instructor?')) return;
    try {
      await client.delete(`/instructors/${id}/delete/`);
      setInstructors(instructors.filter((i) => i.id !== id));
      toast.success('Deleted');
    } catch { toast.error('Failed to delete'); }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Instructors</h1>
        <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2"><Plus size={18} /> Add Instructor</button>
      </div>

      {loading ? <div className="text-center py-20 text-gray-500">Loading...</div> : instructors.length === 0 ? (
        <div className="card text-center py-10">
          <Users size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">No instructors yet.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {instructors.map((inst) => (
            <div key={inst.id} className="card flex items-center justify-between">
              <div>
                <h3 className="font-semibold">{inst.user?.first_name} {inst.user?.last_name}</h3>
                <p className="text-sm text-gray-500">{inst.user?.email} &middot; {inst.user?.phone}</p>
                {inst.license_number && <p className="text-xs text-gray-400">License: {inst.license_number}</p>}
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={inst.is_active !== false ? 'success' : 'danger'}>{inst.is_active !== false ? 'Active' : 'Inactive'}</Badge>
                <button onClick={() => handleDelete(inst.id)} className="text-red-500 text-sm hover:underline">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Add Instructor">
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">First Name *</label><input type="text" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} className="input-field" required /></div>
            <div><label className="label">Last Name *</label><input type="text" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} className="input-field" required /></div>
          </div>
          <div><label className="label">Email *</label><input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="input-field" required /></div>
          <div><label className="label">Phone</label><input type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="input-field" /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">License Number</label><input type="text" value={form.license_number} onChange={(e) => setForm({ ...form, license_number: e.target.value })} className="input-field" /></div>
            <div><label className="label">Experience (years)</label><input type="number" value={form.experience_years} onChange={(e) => setForm({ ...form, experience_years: e.target.value })} className="input-field" min="0" /></div>
          </div>
          {branches.length > 0 && (
            <div><label className="label">Branch</label><select value={form.branch} onChange={(e) => setForm({ ...form, branch: e.target.value })} className="input-field"><option value="">Select branch</option>{branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}</select></div>
          )}
          <button type="submit" disabled={submitting} className="btn-primary w-full">{submitting ? 'Creating...' : 'Create Instructor'}</button>
        </form>
      </Modal>
    </div>
  );
}
