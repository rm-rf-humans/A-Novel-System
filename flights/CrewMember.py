class CrewMember:
    def __init__(self, crew_id, name, role, contact_info):
        try:
            if not isinstance(crew_id, int):
                raise TypeError("Crew ID must be an integer.")
            if not all(isinstance(arg, str) for arg in [name, role, contact_info]):
                raise TypeError("Name, role, and contact info must all be strings.")
            if "@" not in contact_info or "." not in contact_info:
                raise ValueError("Invalid email format for contact_info.")

            self.crew_id = crew_id
            self.name = name
            self.role = role
            self.contact_info = contact_info
            self.assigned_flight = None
            self.status = "Available"

            print(f"crew id is {self.crew_id}, name is {self.name}, role is {self.role}, contact info is {self.contact_info}")

        except (TypeError, ValueError) as e:
            print(f"Initialization Error: {e}")

    def assign_flight(self, flight_id):
        try:
            if not isinstance(flight_id, str):
                raise TypeError("Flight ID must be a string.")
            if self.status == "On Duty":
                raise Exception(f"{self.name} is already assigned to flight {self.assigned_flight}.")

            self.assigned_flight = flight_id
            self.status = "On Duty"
            print(f"{self.name} has been assigned to flight {flight_id}.")

        except (TypeError, Exception) as e:
            print(f"Assignment Error: {e}")

    def view_schedule(self):
        try:
            if self.assigned_flight:
                print(f"{self.name}'s assigned flight: {self.assigned_flight}")
            else:
                print(f"{self.name} has no assigned flights.")
        except Exception as e:
            print(f"Schedule Viewing Error: {e}")

    def update_status(self, new_status):
        try:
            if not isinstance(new_status, str):
                raise TypeError("Status must be a string.")

            valid_statuses = ["Available", "On Duty", "Resting", "Boarding Passengers"]
            if new_status not in valid_statuses:
                raise ValueError(f"'{new_status}' is not a valid status. Valid options are: {valid_statuses}")

            self.status = new_status
            print(f"{self.name}'s status updated to: {new_status}")

        except (TypeError, ValueError) as e:
            print(f"Status Update Error: {e}")



""" crew1 = CrewMember(crew_id= 164, name="Medhat Shalaby", role="Pilot", contact_info="medhat.shalaby@mbappe.com")
crew1.view_schedule()
crew1.assign_flight("FL007")
crew1.view_schedule()
crew1.update_status("Resting")

crew2 = CrewMember(crew_id=199, name="Taylor Swift", role="Flight Attendant", contact_info="Taylor.swift@fayrouz.com")
crew2.assign_flight("FL1213")
crew2.view_schedule()
crew2.update_status("Boarding Passengers") """


