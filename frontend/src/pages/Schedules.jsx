import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { Trash2, Plus, Clock } from 'lucide-react';

const Schedules = () => {
    const [schedules, setSchedules] = useState([]);
    const [patterns, setPatterns] = useState([]);
    const [newSch, setNewSch] = useState({ school_id: 1, day_of_week: 4, time_point: "07:30", pattern_id: 1 });

    const fetchData = async () => {
        try {
            const [schRes, patRes] = await Promise.all([
                api.get('/schedules/'),
                api.get('/patterns/')
            ]);
            setSchedules(schRes.data);
            setPatterns(patRes.data);
        } catch (err) { console.error(err); }
    };

    const handleAdd = async (e) => {
        e.preventDefault();
        try {
            await api.post('/schedules/', newSch);
            fetchData();
            alert("✅ Đã thêm lịch thành công!");
        } catch (err) { alert("❌ Lỗi: Không thể thêm lịch!"); }
    };

    const handleDelete = async (id) => {
        if (!confirm("Bạn có chắc chắn muốn xóa lịch này?")) return;
        try {
            await api.delete(`/schedules/${id}`);
            fetchData();
        } catch (err) { alert("❌ Lỗi khi xóa!"); }
    };

    useEffect(() => { fetchData(); }, []);

    return (
        <div className="p-8">
            <h1 className="text-2xl font-bold mb-6 text-slate-800">Quản lý lịch reo chuông</h1>

            {/* Form */}
            <div className="bg-white p-6 rounded-2xl shadow-sm mb-8 border border-gray-200">
                <form onSubmit={handleAdd} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                    <div>
                        <label className="block text-xs font-bold text-gray-500 mb-1">GIỜ REO</label>
                        <input type="time" className="w-full border p-2 rounded-lg" 
                            value={newSch.time_point} onChange={e => setNewSch({...newSch, time_point: e.target.value})} />
                    </div>
                    <div>
                        <label className="block text-xs font-bold text-gray-500 mb-1">THỨ TRONG TUẦN</label>
                        <select className="w-full border p-2 rounded-lg" value={newSch.day_of_week}
                            onChange={e => setNewSch({...newSch, day_of_week: parseInt(e.target.value)})}>
                            {[0,1,2,3,4,5,6].map(d => <option key={d} value={d}>Thứ {d + 2 == 8 ? "CN" : d + 2}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="block text-xs font-bold text-gray-500 mb-1">KIỂU CHUÔNG (PATTERN)</label>
                        <select className="w-full border p-2 rounded-lg" value={newSch.pattern_id}
                            onChange={e => setNewSch({...newSch, pattern_id: parseInt(e.target.value)})}>
                            {patterns.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                        </select>
                    </div>
                    <button className="bg-blue-600 text-white font-bold py-2 rounded-lg hover:bg-blue-700 transition">LƯU LỊCH</button>
                </form>
            </div>

            {/* List */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-slate-50 border-b">
                        <tr>
                            <th className="p-4 text-xs font-bold text-gray-500 uppercase">Thời gian</th>
                            <th className="p-4 text-xs font-bold text-gray-500 uppercase">Thứ</th>
                            <th className="p-4 text-xs font-bold text-gray-500 uppercase">Kiểu reo</th>
                            <th className="p-4 text-xs font-bold text-gray-500 uppercase">Xóa</th>
                        </tr>
                    </thead>
                    <tbody>
                        {schedules.map(s => (
                            <tr key={s.id} className="border-b last:border-0 hover:bg-gray-50 transition">
                                <td className="p-4 font-mono font-bold text-blue-600">{s.time_point}</td>
                                <td className="p-4 text-gray-600 font-medium">Thứ {s.day_of_week + 2 == 8 ? "CN" : s.day_of_week + 2}</td>
                                <td className="p-4"><span className="bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-xs font-bold">{s.pattern?.name}</span></td>
                                <td className="p-4">
                                    <button onClick={() => handleDelete(s.id)} className="text-red-400 hover:text-red-600 transition">
                                        <Trash2 size={18} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Schedules;