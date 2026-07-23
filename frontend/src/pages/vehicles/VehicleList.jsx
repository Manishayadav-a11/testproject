import { useState, useEffect } from 'react';
import client from '../../api/client';
import Badge from '../../components/ui/Badge';
import { Car, Plus } from 'lucide-react';
import Modal from '../../components/ui/Modal';
import toast from 'react-hot-toast';

export default function VehicleList() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ registration_number: '', vehicle_type: 'LMV', make: '', model: '', year: '', color: '', branch: '' });
  const [branches, setBranches] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    client.get('/vehicles/').then((r) => setVehicles(Array.isArray(r.data) ? r.data : r.data?.results || [])).catch(() => {}).finally(() => setLoading(false));
    client.get('/branches/').then((r) => setBranches(Array.isArray(r.data) ? r.data : r.data?.results || [])).catch(() => {});
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await client.post('/vehicles/', form);
      toast.success('Vehicle added!');
      setShowCreate(false);
      setForm({ registration_number: '', vehicle_type: 'LMV', make: '', model: '', year: '', color: '', branch: '' });
      const r = await client.get('/vehicles/');
      setVehicles(Array.isArray(r.data) ? r.data : r.data?.results || []);
    } catch (err) {
      const data = err.response?.data;
      toast.error(typeof data === 'object' ? Object.values(data).flat().join(', ') : 'Failed');
    } finally { setSubmitting(false); }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this vehicle?')) return;
    try {
      await client.delete(`/vehicles/${id}/delete/`);
      setVehicles(vehicles.filter((v) => v.id !== id));
      toast.success('Deleted');
    } catch { toast.error('Failed to delete'); }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Vehicles</h1>
        <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2"><Plus size={18} /> Add Vehicle</button>
      </div>

      {loading ? <div className="text-center py-20 text-gray-500">Loading...</div> : vehicles.length === 0 ? (
        <div className="card text-center py-10">
          <Car size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">No vehicles yet.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {vehicles.map((v) => (
            <div key={v.id} className="card flex items-center justify-between">
              <div>
                <h3 className="font-semibold">{v.make} {v.model} ({v.year})</h3>
                <p className="text-sm text-gray-500">{v.registration_number} &middot; {v.vehicle_type}</p>
                {v.color && <p className="text-xs text-gray-400">Color: {v.color}</p>}
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={v.is_active !== false ? 'success' : 'danger'}>{v.is_active !== false ? 'Active' : 'Inactive'}</Badge>
                <button onClick={() => handleDelete(v.id)} className="text-red-500 text-sm hover:underline">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Add Vehicle">
        <form onSubmit={handleCreate} className="space-y-4">
          <div><label className="label">Registration Number *</label><input type="text" value={form.registration_number} onChange={(e) => setForm({ ...form, registration_number: e.target.value })} className="input-field" required placeholder="MH 01 AB 1234" /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Vehicle Type</label><select value={form.vehicle_type} onChange={(e) => setForm({ ...form, vehicle_type: e.target.value })} className="input-field"><option>LMV</option><option>HMV</option><option>MCWG</option><option>MCWOG</option></select></div>
            <div><label className="label">Year</label><input type="number" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} className="input-field" min="2000" max="2030" /></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Make</label><input type="text" value={form.make} onChange={(e) => setForm({ ...form, make: e.target.value })} className="input-field" placeholder="Maruti" /></div>
            <div><label className="label">Model</label><input type="text" value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })} className="input-field" placeholder="Swift" /></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Color</label><input type="text" value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })} className="input-field" /></div>
            {branches.length > 0 && (
              <div><label className="label">Branch</label><select value={form.branch} onChange={(e) => setForm({ ...form, branch: e.target.value })} className="input-field"><option value="">Select branch</option>{branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}</select></div>
            )}
          </div>
          <button type="submit" disabled={submitting} className="btn-primary w-full">{submitting ? 'Adding...' : 'Add Vehicle'}</button>
        </form>
      </Modal>
    </div>
  );
}
