import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000', // Sếp kiểm tra xem Backend có đang chạy ở cổng 8000 không nhé
});

export default api;