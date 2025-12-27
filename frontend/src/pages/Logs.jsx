import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { History, CheckCircle2, XCircle, Clock, MousePointer2 } from 'lucide-react';

const Logs = () => {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await api.get('/logs/');
                setLogs(res.data);
            } catch (err) { console.error("Lỗi tải nhật ký", err); }
        };
        fetchLogs();
    }, []);

    return (
        <div className="p-4 md:p-8">
            <h1 className="text-3xl font-black text-slate-800 mb-8 uppercase tracking-tight">Nhật ký reo chuông</h1>
            
            <div className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-slate-50 border-b border-slate-100">
                        <tr>
                            <th className="p-5 text-xs font-black text-slate-400 uppercase tracking-widest">Thời gian</th>
                            <th className="p-5 text-xs font-black text-slate-400 uppercase tracking-widest">Loại lệnh</th>
                            <th className="p-5 text-xs font-black text-slate-400 uppercase tracking-widest text-center">Trạng thái</th>
                            <th className="p-5 text-xs font-black text-slate-400 uppercase tracking-widest">Chi tiết</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs.map(log => (
                            <tr key={log.id} className="border-b border-slate-50 hover:bg-blue-50/20 transition-colors">
                                <td className="p-5 font-bold text-slate-700">
                                    {new Date(log.created_at).toLocaleString('vi-VN')}
                                </td>
                                <td className="p-5">
                                    {log.event_type === 'MANUAL' ? 
                                        <span className="flex items-center text-orange-600 font-black text-xs uppercase"><MousePointer2 size={14} className="mr-1"/> Bấm tay</span> :
                                        <span className="flex items-center text-blue-600 font-black text-xs uppercase"><Clock size={14} className="mr-1"/> Tự động</span>
                                    }
                                </td>
                                <td className="p-5">
                                    {log.status === 'SUCCESS' ? 
                                        <CheckCircle2 className="mx-auto text-green-500" size={20} /> : 
                                        <XCircle className="mx-auto text-red-500" size={20} />
                                    }
                                </td>
                                <td className="p-5 text-sm text-slate-500 italic font-medium">{log.message}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Logs;