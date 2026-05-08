export interface TripDetails {
    origin: string;
    destination: string;
    distance: number; // in miles
    startTime: Date;
    endTime: Date;
    breaks: BreakDetail[];
}

export interface BreakDetail {
    start: Date;
    end: Date;
}

export interface RouteInstructions {
    instructions: string[];
    estimatedArrival: Date;
}

export interface EldLog {
    date: Date;
    status: 'Driving' | 'On Duty' | 'Off Duty';
    duration: number; // in minutes
}