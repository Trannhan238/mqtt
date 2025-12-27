import React, { useState } from 'react';
import api from '../api/axios';

const Login = () => {
    const [creds, setCreds] = useState({ username: '', password: '' });
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('username', creds.username);
            formData.append('password', creds.password);

            const res = await api.post('/auth/login', formData);
            localStorage.setItem('token', res.data.access_token);
            window.location.href = '/';
        } catch (err) {
            alert("Đăng nhập thất bại. Kiểm tra lại tài khoản!");
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-900 px-4">
            <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-slate-800">Bell IoT Pro</h2>
                    <p className="text-gray-500 mt-2">Đăng nhập để quản lý hệ thống</p>
                </div>
                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Tên đăng nhập</label>
                        <input type="text" required className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                            onChange={e => setCreds({...creds, username: e.target.value})} />
                    </div>
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Mật khẩu</label>
                        <input type="password" required className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                            onChange={e => setCreds({...creds, password: e.target.value})} />
                    </div>
                    <button 
                        disabled={loading}
                        className="w-full bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition-all active:scale-95 shadow-lg shadow-blue-200"
                    >
                        {loading ? "Đang xử lý..." : "VÀO HỆ THỐNG"}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Login;