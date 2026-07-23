import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import toast from 'react-hot-toast';

export default function InstituteCreate() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', contact_phone: '', contact_email: '', description: '', website: '', license_number: '', commission_rate: '10' });
  const [logo, setLogo] = useState(null);
  const [licenseDoc, setLicenseDoc] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => { if (v) fd.append(k, v); });
      if (logo) fd.append('logo', logo);
      if (licenseDoc) fd.append('license_document', licenseDoc);
      await client.post('/institutes/create/', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      toast.success('Institute created! Awaiting admin approval.');
      navigate('/dashboard/institute');
    } catch (err) {
      const data = err.response?.data;
      toast.error(typeof data === 'object' ? Object.values(data).flat().join(', ') : 'Failed to create institute');
    } finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Create Institute</h1>
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4" encType="multipart/form-data">
          <div><label className="label">Institute Name *</label><input type="text" name="name" value={form.name} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Description</label><textarea name="description" value={form.description} onChange={handleChange} className="input-field" rows={4} /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Contact Phone *</label><input type="tel" name="contact_phone" value={form.contact_phone} onChange={handleChange} className="input-field" required /></div>
            <div><label className="label">Contact Email</label><input type="email" name="contact_email" value={form.contact_email} onChange={handleChange} className="input-field" /></div>
          </div>
          <div><label className="label">Website</label><input type="url" name="website" value={form.website} onChange={handleChange} className="input-field" placeholder="https://..." /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">License Number</label><input type="text" name="license_number" value={form.license_number} onChange={handleChange} className="input-field" /></div>
            <div><label className="label">Commission Rate (%)</label><input type="number" name="commission_rate" value={form.commission_rate} onChange={handleChange} className="input-field" min="0" max="100" step="0.5" /></div>
          </div>
          <div>
            <label className="label">Institute Logo</label>
            <input type="file" accept="image/*" onChange={(e) => setLogo(e.target.files[0])} className="input-field file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-primary-100 file:text-primary-700 hover:file:bg-primary-200" />
            {logo && <p className="text-xs text-gray-500 mt-1">{logo.name}</p>}
          </div>
          <div>
            <label className="label">License Document</label>
            <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={(e) => setLicenseDoc(e.target.files[0])} className="input-field file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-primary-100 file:text-primary-700 hover:file:bg-primary-200" />
            {licenseDoc && <p className="text-xs text-gray-500 mt-1">{licenseDoc.name}</p>}
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? 'Creating...' : 'Create Institute'}</button>
        </form>
      </div>
    </div>
  );
}
