import { useState } from 'react';
import axios from 'axios';

const useEld = () => {
    const [tripDetails, setTripDetails] = useState(null);
    const [routeInstructions, setRouteInstructions] = useState(null);
    const [eldLogs, setEldLogs] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const submitTripDetails = async (details) => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post('/api/trips/', details);
            setTripDetails(response.data);
            setRouteInstructions(response.data.routeInstructions);
            setEldLogs(response.data.eldLogs);
        } catch (err) {
            setError(err.response ? err.response.data : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return {
        tripDetails,
        routeInstructions,
        eldLogs,
        loading,
        error,
        submitTripDetails,
    };
};

export default useEld;