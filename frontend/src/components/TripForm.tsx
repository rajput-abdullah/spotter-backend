import React, { useState } from 'react';

const TripForm: React.FC = () => {
    const [tripDetails, setTripDetails] = useState({
        origin: '',
        destination: '',
        startDate: '',
        endDate: '',
        driverName: '',
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setTripDetails({
            ...tripDetails,
            [name]: value,
        });
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        try {
            const response = await fetch('/api/trips', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(tripDetails),
            });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            console.log('Trip data submitted successfully:', data);
        } catch (error) {
            console.error('Error submitting trip data:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>
                    Origin:
                    <input type="text" name="origin" value={tripDetails.origin} onChange={handleChange} required />
                </label>
            </div>
            <div>
                <label>
                    Destination:
                    <input type="text" name="destination" value={tripDetails.destination} onChange={handleChange} required />
                </label>
            </div>
            <div>
                <label>
                    Start Date:
                    <input type="date" name="startDate" value={tripDetails.startDate} onChange={handleChange} required />
                </label>
            </div>
            <div>
                <label>
                    End Date:
                    <input type="date" name="endDate" value={tripDetails.endDate} onChange={handleChange} required />
                </label>
            </div>
            <div>
                <label>
                    Driver Name:
                    <input type="text" name="driverName" value={tripDetails.driverName} onChange={handleChange} required />
                </label>
            </div>
            <button type="submit">Submit Trip</button>
        </form>
    );
};

export default TripForm;