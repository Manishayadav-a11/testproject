import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Profile from './pages/auth/Profile';
import InstituteList from './pages/institutes/InstituteList';
import InstituteDetail from './pages/institutes/InstituteDetail';
import InstituteCreate from './pages/institutes/InstituteCreate';
import InstituteDashboard from './pages/institutes/InstituteDashboard';
import CourseList from './pages/courses/CourseList';
import CourseDetail from './pages/courses/CourseDetail';
import CourseCreate from './pages/courses/CourseCreate';
import BookingList from './pages/bookings/BookingList';
import BookingCreate from './pages/bookings/BookingCreate';
import BookingDetail from './pages/bookings/BookingDetail';
import PaymentHistory from './pages/payments/PaymentHistory';
import PaymentDetail from './pages/payments/PaymentDetail';
import ReviewList from './pages/reviews/ReviewList';
import ReviewCreate from './pages/reviews/ReviewCreate';
import StudentDashboard from './pages/student/StudentDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="institutes" element={<InstituteList />} />
        <Route path="institutes/:id" element={<InstituteDetail />} />
        <Route path="courses" element={<CourseList />} />
        <Route path="courses/:id" element={<CourseDetail />} />
        
        <Route element={<ProtectedRoute />}>
          <Route path="profile" element={<Profile />} />
          <Route path="institutes/create" element={<InstituteCreate />} />
          <Route path="dashboard/institute" element={<InstituteDashboard />} />
          <Route path="courses/create" element={<CourseCreate />} />
          <Route path="bookings" element={<BookingList />} />
          <Route path="bookings/create" element={<BookingCreate />} />
          <Route path="bookings/:id" element={<BookingDetail />} />
          <Route path="payments" element={<PaymentHistory />} />
          <Route path="payments/:id" element={<PaymentDetail />} />
          <Route path="reviews" element={<ReviewList />} />
          <Route path="reviews/create" element={<ReviewCreate />} />
          <Route path="dashboard/student" element={<StudentDashboard />} />
          <Route path="dashboard/admin" element={<AdminDashboard />} />
        </Route>
      </Route>
    </Routes>
  );
}
