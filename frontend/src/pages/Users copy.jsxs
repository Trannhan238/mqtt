import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { UserPlus, ShieldCheck, Trash2, UserCog, UserCheck } from 'lucide-react';

const Users = () => {
    const [users, setUsers] = useState([]);
    const [schools, setSchools] = useState([]);
    const [loading, setLoading] = useState(false);
    const [currentUser, setCurrentUser] = useState(null); // Lưu thông tin người đang đăng nhập

    const fetchData = async () => {
        setLoading(true);
        try {
            const [uRes, sRes] = await Promise.all([api.get('/users/'), api.get('/schools/')]);
            setUsers(uRes.data);
            setSchools(sRes.data);
        } catch (err) { console.error("Lỗi tải dữ liệu", err); }
        setLoading(false);
    };

    useEffect(() => { 
        fetchData();
        // Lấy role từ token để ẩn/hiện chức năng
        const token = localStorage.getItem('token');
        if (token) {
            const payload = JSON.parse(atob(token.split('.')[1]));
            setCurrentUser(payload);
        }
    }, []);

    return (
        <div className="min-h-screen bg-slate-50 p-4 md:p-8">
            <div className="flex justify-between items-end mb-10">
                <div>
                    <h1 className="text-3xl font-black text-slate-800 tracking-tight uppercase">Nhân sự hệ thống</h1>
                    <p className="text-slate-500 font-medium italic">
                        {currentUser?.role === 'admin' ? "Quản lý tài khoản toàn ngành" : `Quản trị đơn vị: ${users[0]?.school?.name || ''}`}
                    </p>
                </div>
                <button className="flex items-center bg-blue-600 text-white px-6 py-3 rounded-2xl font-black text-sm hover:bg-blue-700 transition-all shadow-lg shadow-blue-200">
                    <UserPlus size={18} className="mr-2"/> THÊM THÀNH VIÊN
                </button>
            </div>

            {/* Danh sách người dùng dạng Card cho hiện đại */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {users.map(u => (
                    <div key={u.id} className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 hover:shadow-md transition-all group">
                        <div className="flex justify-between items-start mb-4">
                            <div className="bg-slate-50 p-3 rounded-2xl text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-500 transition-colors">
                                <UserCog size={24} />
                            </div>
                            <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                                u.role === 'admin' ? 'bg-purple-100 text-purple-600' : 'bg-blue-100 text-blue-600'
                            }`}>
                                {u.role === 'admin' ? 'Hệ thống' : 'Trường học'}
                            </span>
                        </div>
                        
                        <div className="mb-6">
                            <h3 className="text-lg font-black text-slate-800 leading-tight">{u.full_name}</h3>
                            <p className="text-sm font-bold text-slate-400">@{u.username}</p>
                        </div>

                        <div className="pt-4 border-t border-slate-50 flex justify-between items-center">
                            <div className="flex items-center text-xs font-bold text-slate-500">
                                <ShieldCheck size={14} className="mr-1 text-green-500" /> Hoạt động
                            </div>
                            <button className="text-slate-300 hover:text-red-500 transition-colors">
                                <Trash2 size={18} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Users;