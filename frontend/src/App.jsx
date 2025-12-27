import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Schedules from './pages/Schedules';
import Login from './pages/Login';
import Users from './pages/Users'; // Sếp sẽ tạo file này sau
import Logs from './pages/Logs';   // Sếp sẽ tạo file này sau
import { 
  LayoutDashboard, CalendarClock, LogOut, 
  Users as UsersIcon, History, Shield, 
  Settings, HardDrive, School 
} from 'lucide-react';

// --- 1. HÀM GIẢI MÃ TOKEN (Để biết sếp là ai) ---
const getAuth = () => {
  const token = localStorage.getItem('token');
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload; // Trả về { sub, role, school_id, ... }
  } catch (e) {
    return null;
  }
};

// --- 2. SIDEBAR THÔNG MINH (Ẩn hiện theo Role) ---
const Sidebar = () => {
  const auth = getAuth();
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  return (
    <div className="w-72 bg-slate-950 text-white min-h-screen p-6 shadow-2xl flex flex-col fixed left-0 top-0 border-r border-slate-800">
      <div className="mb-10 px-2">
        <h2 className="text-2xl font-black text-blue-500 italic tracking-tighter">BELL IOT PRO</h2>
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">Hệ thống điều khiển trung tâm</p>
      </div>
      
      <nav className="space-y-1 flex-1">
        {/* Menu cho tất cả mọi người */}
        <MenuLink to="/" icon={<LayoutDashboard size={20}/>} label="Bảng điều khiển" />
        <MenuLink to="/schedules" icon={<CalendarClock size={20}/>} label="Lịch reo chuông" />
        <MenuLink to="/logs" icon={<History size={20}/>} label="Nhật ký reo" />
        
        <div className="my-4 border-t border-slate-800 pt-4">
           <p className="text-[10px] font-black text-slate-600 uppercase mb-2 px-3">Quản trị</p>
           <MenuLink to="/users" icon={<UsersIcon size={20}/>} label="Người dùng" />
        </div>

        {/* CHỈ ADMIN SỞ MỚI THẤY MỤC NÀY (Giống ảnh sếp gửi) */}
        {auth?.role === 'admin' && (
          <div className="space-y-1">
             <MenuLink to="/schools" icon={<School size={20}/>} label="Trường học" />
             <MenuLink to="/firmware" icon={<HardDrive size={20}/>} label="Firmware" />
             <MenuLink to="/settings" icon={<Settings size={20}/>} label="Hệ thống" />
          </div>
        )}
      </nav>
      
      <div className="mt-auto pt-6 border-t border-slate-800">
        <div className="mb-4 px-3">
            <p className="text-xs font-bold text-blue-400">Xin chào, {auth?.sub}</p>
            <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-slate-400 uppercase font-black">
                {auth?.role === 'admin' ? 'Quản trị Sở' : 'Quản trị Trường'}
            </span>
        </div>
        <button onClick={handleLogout} className="w-full flex items-center space-x-3 p-3 text-red-400 hover:bg-red-950/30 rounded-xl transition-all">
          <LogOut size={20} />
          <span className="font-bold">Đăng xuất</span>
        </button>
      </div>
    </div>
  );
};

// Helper để code Menu đỡ dài
const MenuLink = ({ to, icon, label }) => (
  <Link to={to} className="flex items-center space-x-3 p-3 hover:bg-slate-900 hover:text-blue-400 rounded-xl transition-all group">
    <span className="text-slate-500 group-hover:text-blue-400">{icon}</span>
    <span className="font-bold text-sm">{label}</span>
  </Link>
);

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" />;
};

// --- 3. APP MAIN ---
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/*" element={
            <PrivateRoute>
              <div className="flex bg-slate-50 min-h-screen">
                <Sidebar />
                {/* ml-72 để né cái sidebar fixed ra sếp nhé */}
                <div className="ml-72 flex-1 p-8">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/schedules" element={<Schedules />} />
                    <Route path="/users" element={<Users />} />
                    <Route path="/logs" element={<Logs />} />
                    
                    {/* Các route trống để tránh lỗi Vite, sếp sẽ làm sau */}
                    <Route path="/schools" element={<div className="font-black text-3xl">QUẢN LÝ TRƯỜNG HỌC</div>} />
                    <Route path="/firmware" element={<div className="font-black text-3xl">CẬP NHẬT FIRMWARE</div>} />
                    
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