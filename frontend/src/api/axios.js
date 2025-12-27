import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
});

// THÊM ĐOẠN NÀY ĐỂ TỰ ĐỘNG GỬI TOKEN TRÊN MỌI API
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;