import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Schedules from './pages/Schedules';
import Login from './pages/Login'; // Sếp nhớ tạo file này ở bước dưới
import { LayoutDashboard, CalendarClock, LogOut } from 'lucide-react';

// Thành phần Sidebar (Tách riêng cho gọn)
const Sidebar = () => {
  const handleLogout = () => {
    localStorage.removeItem('token'); // Xóa token
    window.location.href = '/login'; // Chuyển về login
  };

  return (
    <div className="w-64 bg-slate-900 text-white p-6 shadow-xl flex-shrink-0 flex flex-col">
      <h2 className="text-2xl font-bold mb-10 text-blue-400">Bell IoT Pro</h2>
      <nav className="space-y-4 flex-1">
        <Link to="/" className="flex items-center space-x-3 p-3 hover:bg-slate-800 rounded-lg transition">
          <LayoutDashboard size={20} />
          <span>Bảng điều khiển</span>
        </Link>
        <Link to="/schedules" className="flex items-center space-x-3 p-3 hover:bg-slate-800 rounded-lg transition">
          <CalendarClock size={20} />
          <span>Lịch reo chuông</span>
        </Link>
      </nav>
      
      {/* Nút Đăng xuất */}
      <button 
        onClick={handleLogout}
        className="flex items-center space-x-3 p-3 text-red-400 hover:bg-red-900/20 rounded-lg transition mt-auto"
      >
        <LogOut size={20} />
        <span>Đăng xuất</span>
      </button>
    </div>
  );
};

// Thành phần bảo vệ Route (Kiểm tra sếp đã đăng nhập chưa)
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Route Đăng nhập - Không có Sidebar */}
        <Route path="/login" element={<Login />} />

        {/* Các Route quản trị - Phải qua PrivateRoute và có Sidebar */}
        <Route 
          path="/*" 
          element={
            <PrivateRoute>
              <div className="flex min-h-screen bg-gray-50 text-slate-900">
                <Sidebar />
                <div className="flex-1 overflow-auto bg-gray-100">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/schedules" element={<Schedules />} />
                    {/* Nếu vào link bậy bạ thì về Dashboard */}
                    <Route path="*" element={<Navigate to="/" />} />
                  </Routes>
                </div>
              </div>
            </PrivateRoute>
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;