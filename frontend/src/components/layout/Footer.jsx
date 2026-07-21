import { Link } from 'react-router-dom';
import { Car, Mail, Phone, MapPin } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Car className="text-primary-400" size={24} />
              <span className="text-xl font-bold text-white">DrivingHub</span>
            </div>
            <p className="text-sm text-gray-400">
              India's leading multi-vendor marketplace connecting students with the best driving institutes.
            </p>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">Quick Links</h3>
            <div className="space-y-2 text-sm">
              <Link to="/institutes" className="block hover:text-primary-400">Find Institutes</Link>
              <Link to="/courses" className="block hover:text-primary-400">Browse Courses</Link>
              <Link to="/register" className="block hover:text-primary-400">Register</Link>
            </div>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">For Business</h3>
            <div className="space-y-2 text-sm">
              <Link to="/register" className="block hover:text-primary-400">List Your Institute</Link>
              <Link to="/dashboard/institute" className="block hover:text-primary-400">Institute Dashboard</Link>
            </div>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">Contact</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2"><Mail size={16} /> support@drivinghub.in</div>
              <div className="flex items-center gap-2"><Phone size={16} /> +91 1800-123-4567</div>
              <div className="flex items-center gap-2"><MapPin size={16} /> India</div>
            </div>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-500">
          © {new Date().getFullYear()} DrivingHub. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
