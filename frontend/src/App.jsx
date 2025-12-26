import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Schedules from './pages/Schedules';
import { LayoutDashboard, CalendarClock } from 'lucide-react';

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-gray-50 text-slate-900">
        {/* Sidebar */}
        <div className="w-64 bg-slate-900 text-white p-6 shadow-xl flex-shrink-0">
          <h2 className="text-2xl font-bold mb-10 text-blue-400">Bell IoT Pro</h2>
          <nav className="space-y-4">
            <Link to="/" className="flex items-center space-x-3 p-3 hover:bg-slate-800 rounded-lg transition">
              <LayoutDashboard size={20} />
              <span>Bảng điều khiển</span>
            </Link>
            <Link to="/schedules" className="flex items-center space-x-3 p-3 hover:bg-slate-800 rounded-lg transition">
              <CalendarClock size={20} />
              <span>Lịch reo chuông</span>
            </Link>
          </nav>
        </div>

        {/* Nội dung chính */}
        <div className="flex-1 overflow-auto bg-gray-100">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/schedules" element={<Schedules />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;