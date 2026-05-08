import axios from 'axios';

const apiClient = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const submitTripDetails = async (tripDetails) => {
    try {
        const response = await apiClient.post('/trips/', tripDetails);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error.message;
    }
};

export const getRouteInstructions = async (tripId) => {
    try {
        const response = await apiClient.get(`/trips/${tripId}/instructions/`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error.message;
    }
};

export const getEldLogs = async (tripId) => {
    try {
        const response = await apiClient.get(`/trips/${tripId}/eld-logs/`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error.message;
    }
};