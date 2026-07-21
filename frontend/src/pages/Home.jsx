import { Link } from 'react-router-dom';
import { Search, Shield, Star, Users, ArrowRight, Car, MapPin, BookOpen } from 'lucide-react';
import { useState, useEffect } from 'react';
import client from '../api/client';

export default function Home() {
  const [featuredInstitutes, setFeaturedInstitutes] = useState([]);
  const [popularCourses, setPopularCourses] = useState([]);

  useEffect(() => {
    client.get('/institutes/featured/').then((r) => setFeaturedInstitutes(r.data?.results || r.data || [])).catch(() => {});
    client.get('/courses/popular/').then((r) => setPopularCourses(r.data?.results || r.data || [])).catch(() => {});
  }, []);

  return (
    <div>
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">Find the Perfect Driving Institute Near You</h1>
            <p className="text-primary-100 text-lg mb-8">Compare courses, read reviews, and book lessons from top-rated driving institutes across India.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/institutes" className="bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-primary-50 transition flex items-center justify-center gap-2">
                <Search size={20} /> Browse Institutes
              </Link>
              <Link to="/register" className="border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white/10 transition flex items-center justify-center gap-2">
                List Your Institute <ArrowRight size={20} />
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { icon: <Car className="text-primary-600" size={32} />, title: 'Verified Institutes', desc: 'All institutes are verified and rated by real students.' },
            { icon: <BookOpen className="text-primary-600" size={32} />, title: 'Multiple Courses', desc: 'From LMV to heavy vehicles, find courses that match your needs.' },
            { icon: <MapPin className="text-primary-600" size={32} />, title: 'Pan-India Coverage', desc: 'Find driving institutes in every major city across India.' },
          ].map((item, i) => (
            <div key={i} className="card text-center">
              <div className="flex justify-center mb-4">{item.icon}</div>
              <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
              <p className="text-gray-600">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {featuredInstitutes.length > 0 && (
        <section className="bg-gray-100 py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-bold">Featured Institutes</h2>
              <Link to="/institutes" className="text-primary-600 hover:underline flex items-center gap-1">View All <ArrowRight size={16} /></Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {featuredInstitutes.slice(0, 3).map((inst) => (
                <Link key={inst.id} to={`/institutes/${inst.id}`} className="card hover:shadow-md transition">
                  <h3 className="font-semibold text-lg mb-1">{inst.name}</h3>
                  <p className="text-gray-500 text-sm mb-2 flex items-center gap-1"><MapPin size={14} /> {inst.city || 'India'}</p>
                  <div className="flex items-center gap-1 text-sm">
                    <Star size={14} className="fill-yellow-400 text-yellow-400" />
                    <span>{inst.average_rating || 'N/A'}</span>
                    <span className="text-gray-400">({inst.review_count || 0} reviews)</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="bg-primary-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Ready to Start Your Driving Journey?</h2>
          <p className="text-primary-100 mb-6">Join thousands of students who found their perfect driving institute.</p>
          <Link to="/register" className="bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-primary-50 transition inline-flex items-center gap-2">
            Get Started <ArrowRight size={20} />
          </Link>
        </div>
      </section>
    </div>
  );
}
