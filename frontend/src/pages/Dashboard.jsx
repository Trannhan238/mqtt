import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { Bell, Wifi, WifiOff, RefreshCw, Cpu, School } from 'lucide-react';

const Dashboard = () => {
    const [devices, setDevices] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchDevices = async () => {
        setLoading(true);
        try {
            const res = await api.get('/devices/'); 
            setDevices(res.data);
        } catch (err) {
            console.error("Lỗi lấy danh sách thiết bị", err);
        }
        setLoading(false);
    };

    const ringNow = async (mac) => {
        try {
            // Sếp có thể thay đổi số hồi chuông (pulses) ở đây
            await api.post(`/devices/${mac}/ring-now?pulses=3`);
            alert("🔔 Lệnh reo chuông đã được gửi tới thiết bị!");
        } catch (err) {
            alert("❌ Lỗi: Không thể điều khiển thiết bị!");
        }
    };

    useEffect(() => {
        fetchDevices();
        const interval = setInterval(fetchDevices, 10000); 
        return () => clearInterval(interval);
    }, []);

    // Hàm format ngày tháng an toàn
    const formatDate = (dateStr) => {
    if (!dateStr) return "Chưa có tín hiệu";
    const date = new Date(dateStr);
    
    // Nếu ngày không hợp lệ, trả về thông báo chờ
    if (isNaN(date.getTime())) return "Đang chờ cập nhật...";

    // Format theo kiểu Việt Nam: 19:45:00 - 26/12
    return new Intl.DateTimeFormat('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        day: '2-digit',
        month: '2-digit',
    }).format(date);
};

    return (
        <div className="min-h-screen bg-slate-50 p-4 md:p-8">
            {/* Header Area */}
            <div className="flex justify-between items-center mb-10">
                <div>
                    <h1 className="text-3xl font-black text-slate-800 tracking-tight">TRẠNG THÁI HỆ THỐNG</h1>
                    <p className="text-slate-500 font-medium">Quản lý và điều khiển chuông thời gian thực</p>
                </div>
                <button 
                    onClick={fetchDevices} 
                    className="group p-3 bg-white rounded-2xl shadow-sm border border-slate-200 hover:border-blue-400 transition-all active:scale-90"
                >
                    <RefreshCw className={`w-6 h-6 ${loading ? "animate-spin text-blue-500" : "text-slate-600 group-hover:text-blue-500"}`} />
                </button>
            </div>

            {/* Device Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {devices.map((device) => (
                    <div 
                        key={device.mac_address} 
                        className={`relative bg-white rounded-3xl shadow-sm border-2 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${
                            device.status === 'online' ? 'border-blue-100 hover:border-blue-300' : 'border-slate-100'
                        }`}
                    >
                        {/* Status Ribbon */}
                        <div className="absolute top-4 right-4">
                            {device.status === 'online' ? (
                                <span className="flex items-center px-3 py-1 bg-green-100 text-green-600 rounded-full text-xs font-black animate-pulse">
                                    <Wifi size={14} className="mr-1" /> ONLINE
                                </span>
                            ) : (
                                <span className="flex items-center px-3 py-1 bg-slate-100 text-slate-400 rounded-full text-xs font-black">
                                    <WifiOff size={14} className="mr-1" /> OFFLINE
                                </span>
                            )}
                        </div>

                        <div className="p-8">
                            {/* Device Icon & Name */}
                            <div className="flex items-center space-x-4 mb-6">
                                <div className={`p-3 rounded-2xl ${device.status === 'online' ? 'bg-blue-50 text-blue-600' : 'bg-slate-50 text-slate-400'}`}>
                                    <Cpu size={32} />
                                </div>
                                <div>
                                    <h2 className="text-xl font-black text-slate-800 uppercase leading-tight">{device.name || "THIẾT BỊ LẠ"}</h2>
                                    <p className="text-xs font-mono font-bold text-slate-400 tracking-widest">{device.mac_address}</p>
                                </div>
                            </div>

                            {/* Info Rows */}
                            <div className="space-y-3 mb-8">
                                <div className="flex items-center text-sm text-slate-600">
                                    <div className="w-8"><School size={16} className="text-slate-400" /></div>
                                    <span className="font-medium mr-2">Trường:</span>
                                    <span className="font-bold text-slate-800">{device.school?.name || "Chưa gán trường"}</span>
                                </div>
                                <div className="flex items-center text-sm text-slate-600">
                                    <div className="w-8 font-bold text-slate-400">🕒</div>
                                    <span className="font-medium mr-2">Cập nhật:</span>
                                    <span className="font-bold text-slate-800">{formatDate(device.last_seen)}</span>
                                </div>
                            </div>

                            {/* Action Button */}
                            <button 
                                onClick={() => ringNow(device.mac_address)}
                                disabled={device.status !== 'online'}
                                className={`w-full flex items-center justify-center py-4 rounded-2xl font-black text-sm tracking-widest transition-all shadow-lg ${
                                    device.status === 'online' 
                                    ? "bg-blue-600 text-white hover:bg-blue-700 active:scale-95 shadow-blue-200" 
                                    : "bg-slate-100 text-slate-300 cursor-not-allowed shadow-none"
                                }`}
                            >
                                <Bell size={20} className="mr-2" /> REO CHUÔNG NGAY
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Empty State */}
            {devices.length === 0 && !loading && (
                <div className="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-slate-200">
                    <p className="text-slate-400 font-bold">Chưa có thiết bị nào trong danh sách...</p>
                </div>
            )}
        </div>
    );
};

export default Dashboard;