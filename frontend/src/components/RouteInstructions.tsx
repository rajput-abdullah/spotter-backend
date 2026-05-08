import React from 'react';

interface RouteInstructionsProps {
    instructions: string;
    eldLogs: string;
}

const RouteInstructions: React.FC<RouteInstructionsProps> = ({ instructions, eldLogs }) => {
    return (
        <div>
            <h2>Route Instructions</h2>
            <pre>{instructions}</pre>
            <h2>ELD Logs</h2>
            <pre>{eldLogs}</pre>
        </div>
    );
};

export default RouteInstructions;