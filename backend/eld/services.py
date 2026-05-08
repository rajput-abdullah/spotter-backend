from datetime import datetime, timedelta

class ELDService:
    def __init__(self, trip_details):
        self.trip_details = trip_details
        self.logs = []

    def calculate_route_instructions(self):
        # Logic to calculate route instructions based on trip details
        start_location = self.trip_details.get('start_location')
        end_location = self.trip_details.get('end_location')
        distance = self.trip_details.get('distance')
        estimated_time = self.calculate_estimated_time(distance)

        instructions = {
            'start_location': start_location,
            'end_location': end_location,
            'distance': distance,
            'estimated_time': estimated_time,
            'route': self.generate_route(start_location, end_location)
        }
        return instructions

    def calculate_estimated_time(self, distance):
        # Assuming an average speed of 50 miles per hour
        average_speed = 50
        hours = distance / average_speed
        return str(timedelta(hours=hours))

    def generate_route(self, start_location, end_location):
        # Placeholder for route generation logic
        return f"Route from {start_location} to {end_location}"

    def generate_eld_logs(self):
        # Logic to generate ELD logs based on trip details and HOS regulations
        start_time = datetime.now()
        driving_time = self.trip_details.get('driving_time', 0)
        rest_time = self.trip_details.get('rest_time', 0)

        self.logs.append({
            'start_time': start_time,
            'end_time': start_time + timedelta(hours=driving_time),
            'status': 'Driving'
        })

        if rest_time > 0:
            self.logs.append({
                'start_time': start_time + timedelta(hours=driving_time),
                'end_time': start_time + timedelta(hours=driving_time + rest_time),
                'status': 'Rest'
            })

        return self.logs

    def validate_trip_details(self):
        # Logic to validate trip details against HOS regulations
        if self.trip_details.get('driving_time') + self.trip_details.get('rest_time') > 14:
            raise ValueError("Total driving and rest time exceeds allowed limits.")
        return True

    def process_trip(self):
        self.validate_trip_details()
        route_instructions = self.calculate_route_instructions()
        eld_logs = self.generate_eld_logs()
        return {
            'route_instructions': route_instructions,
            'eld_logs': eld_logs
        }
