class CrewMember:
    def __init__(self, crew_id, name, role, contact_info):
        self.crew_id = crew_id
        self.name = name
        self.role = role
        self.contact_info = contact_info
        self.assigned_flight = None
        self.status = "Available"
        print (f"crew id is {self.crew_id}, name is {self.name}, role is {self.role}, contact info is {self.contact_info}")

    def assign_flight(self, flight_id):
        self.assigned_flight = flight_id
        self.status = "On Duty"
        print(f"{self.name} has been assigned to flight {flight_id}.")

    def view_schedule(self):
        if self.assigned_flight:
            print(f"{self.name}'s assigned flight: {self.assigned_flight}")
        else:
            print(f"{self.name} has no assigned flights.")

    def update_status(self, new_status):
        self.status = new_status
        print(f"{self.name}'s status updated to: {new_status}")


""" crew1 = CrewMember(crew_id= 164, name="Medhat Shalaby", role="Pilot", contact_info="medhat.shalaby@mbappe.com")
crew1.view_schedule()
crew1.assign_flight("FL007")
crew1.view_schedule()
crew1.update_status("Resting")

crew2 = CrewMember(crew_id=199, name="Taylor Swift", role="Flight Attendant", contact_info="Taylor.swift@fayrouz.com")
crew2.assign_flight("FL1213")
crew2.view_schedule()
crew2.update_status("Boarding Passengers") """


