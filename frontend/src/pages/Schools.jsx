import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { School, Snowflake, Sun, Clock, Save } from 'lucide-react';

const Schools = () => {
    const [schools, setSchools] = useState([]);

    const fetchSchools = async () => {
        const res = await api.get('/schools/');
        setSchools(res.data);
    };

    useEffect(() => { fetchSchools(); }, []);

    const toggleWinter = async (id, currentStatus) => {
        try {
            await api.patch(`/schools/${id}`, { use_seasonal_config: !currentStatus });
            fetchSchools();
        } catch (err) { alert("Lỗi cập nhật cấu hình!"); }
    };

    return (
        <div className="p-8">
            <h1 className="text-3xl font-black text-slate-800 mb-8 uppercase tracking-tight">Danh sách đơn vị</h1>
            
            <div className="grid grid-cols-1 gap-6">
                {schools.map(s => (
                    <div key={s.id} className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center">
                        <div className="flex items-center space-x-6 mb-6 md:mb-0">
                            <div className="bg-blue-50 p-4 rounded-2xl text-blue-600">
                                <School size={40} />
                            </div>
                            <div>
                                <h2 className="text-2xl font-black text-slate-800">{s.name}</h2>
                                <p className="text-slate-400 font-bold">{s.address || "Chưa cập nhật địa chỉ"}</p>
                            </div>
                        </div>

                        {/* Panel cấu hình mùa đông */}
                        <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 flex items-center space-x-8">
                            <div className="text-center">
                                <p className="text-[10px] font-black text-slate-400 uppercase mb-2">Trạng thái mùa</p>
                                <button 
                                    onClick={() => toggleWinter(s.id, s.use_seasonal_config)}
                                    className={`flex items-center px-4 py-2 rounded-xl font-black text-xs transition-all ${
                                        s.use_seasonal_config ? "bg-blue-600 text-white shadow-lg shadow-blue-100" : "bg-orange-100 text-orange-600"
                                    }`}
                                >
                                    {s.use_seasonal_config ? <><Snowflake size={14} className="mr-2"/> ĐANG ÁP DỤNG GIỜ LẠNH</> : <><Sun size={14} className="mr-2"/> GIỜ BÌNH THƯỜNG</>}
                                </button>
                            </div>
                            
                            <div className="border-l border-slate-200 pl-8">
                                <p className="text-[10px] font-black text-slate-400 uppercase mb-1">Độ trễ (Offset)</p>
                                <div className="flex items-center text-xl font-black text-slate-700">
                                    <Clock size={18} className="mr-2 text-slate-400"/> {s.winter_offset_minutes} phút
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Schools;