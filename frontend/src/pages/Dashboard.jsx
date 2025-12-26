import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { Bell, Wifi, WifiOff, RefreshCw } from 'lucide-react';

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
            await api.post(`/devices/${mac}/ring-now?pulses=3`);
            alert("🔔 Đã phát lệnh reo chuông tới thiết bị!");
        } catch (err) {
            alert("❌ Lỗi: Không thể gửi lệnh reo!");
        }
    };

    useEffect(() => {
        fetchDevices();
        const interval = setInterval(fetchDevices, 10000); // Check online mỗi 10s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-slate-800">Trạng thái hệ thống</h1>
                <button onClick={fetchDevices} className="p-2 bg-white rounded-full shadow hover:bg-gray-50 transition">
                    <RefreshCw className={loading ? "animate-spin text-blue-500" : "text-gray-600"} />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {devices.map((device) => (
                    <div key={device.mac_address} className="bg-white rounded-2xl shadow-sm p-6 border border-gray-200">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h2 className="text-xl font-bold text-slate-700">{device.name || "Thiết bị chưa đặt tên"}</h2>
                                <p className="text-sm font-mono text-gray-400">{device.mac_address}</p>
                            </div>
                            {device.status === 'online' ? 
                                <span className="flex items-center px-3 py-1 bg-green-100 text-green-600 rounded-full text-xs font-bold">
                                    <Wifi size={14} className="mr-1" /> ONLINE
                                </span> : 
                                <span className="flex items-center px-3 py-1 bg-red-100 text-red-600 rounded-full text-xs font-bold">
                                    <WifiOff size={14} className="mr-1" /> OFFLINE
                                </span>
                            }
                        </div>
                        
                        <div className="space-y-2 mb-6">
                            <p className="text-sm text-gray-600">🏫 Trường: <span className="font-semibold">{device.school?.name || "N/A"}</span></p>
                            <p className="text-sm text-gray-600">🕒 Cập nhật: {new Date(device.last_seen).toLocaleString('vi-VN')}</p>
                        </div>

                        <button 
                            onClick={() => ringNow(device.mac_address)}
                            disabled={device.status !== 'online'}
                            className={`w-full flex items-center justify-center py-3 rounded-xl font-bold transition-all ${
                                device.status === 'online' 
                                ? "bg-blue-600 text-white hover:bg-blue-700 active:scale-95 shadow-lg shadow-blue-200" 
                                : "bg-gray-100 text-gray-400 cursor-not-allowed"
                            }`}
                        >
                            <Bell size={18} className="mr-2" /> REO CHUÔNG NGAY
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Dashboard;