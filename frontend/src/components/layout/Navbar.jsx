import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, Car, ChevronDown, LogOut, User, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/');
    setProfileOpen(false);
  };

  const dashboardPath = {
    admin: '/dashboard/admin',
    institute_owner: '/dashboard/institute',
    instructor: '/dashboard/institute',
    student: '/dashboard/student',
  };

  return (
    <nav className="bg-white shadow-sm border-b sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <Car className="text-primary-600" size={28} />
            <span className="text-xl font-bold text-primary-600">DrivingHub</span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            <Link to="/institutes" className="text-gray-600 hover:text-primary-600 font-medium">Institutes</Link>
            <Link to="/courses" className="text-gray-600 hover:text-primary-600 font-medium">Courses</Link>
            {user && (
              <>
                <Link to="/bookings" className="text-gray-600 hover:text-primary-600 font-medium">Bookings</Link>
                <Link to="/reviews" className="text-gray-600 hover:text-primary-600 font-medium">Reviews</Link>
              </>
            )}
          </div>

          <div className="hidden md:flex items-center gap-4">
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100"
                >
                  <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-medium">
                    {user.first_name?.[0]}{user.last_name?.[0]}
                  </div>
                  <span className="text-sm font-medium">{user.first_name}</span>
                  <ChevronDown size={16} />
                </button>
                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border py-1">
                    <Link
                      to={dashboardPath[user.role] || '/profile'}
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50"
                    >
                      <LayoutDashboard size={16} /> Dashboard
                    </Link>
                    <Link
                      to="/profile"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50"
                    >
                      <User size={16} /> Profile
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-gray-50 w-full"
                    >
                      <LogOut size={16} /> Logout
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link to="/login" className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600">Login</Link>
                <Link to="/register" className="btn-primary text-sm">Sign Up</Link>
              </div>
            )}
          </div>

          <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden p-2">
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t bg-white">
          <div className="px-4 py-3 space-y-2">
            <Link to="/institutes" onClick={() => setMobileOpen(false)} className="block py-2 text-gray-600 hover:text-primary-600">Institutes</Link>
            <Link to="/courses" onClick={() => setMobileOpen(false)} className="block py-2 text-gray-600 hover:text-primary-600">Courses</Link>
            {user ? (
              <>
                <Link to="/bookings" onClick={() => setMobileOpen(false)} className="block py-2 text-gray-600 hover:text-primary-600">Bookings</Link>
                <Link to="/reviews" onClick={() => setMobileOpen(false)} className="block py-2 text-gray-600 hover:text-primary-600">Reviews</Link>
                <Link to="/profile" onClick={() => setMobileOpen(false)} className="block py-2 text-gray-600 hover:text-primary-600">Profile</Link>
                <button onClick={handleLogout} className="block py-2 text-red-600">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" onClick={() => setMobileOpen(false)} className="block py-2 text-gray-600">Login</Link>
                <Link to="/register" onClick={() => setMobileOpen(false)} className="block py-2 text-primary-600 font-medium">Sign Up</Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
