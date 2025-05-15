class CrewRegistry:
    """Singleton registry for crew members"""
    _instance = None
    _crew_members = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def add_crew_member(self, crew_member):
        self._crew_members[crew_member.crew_id] = crew_member

    def get_crew_member(self, crew_id):
        return self._crew_members.get(crew_id)

    def all_crew(self):
        return list(self._crew_members.values())

class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

    def has_permission(self, action):
        permissions = {
            "admin": ["add", "remove", "view", "update"],
            "staff": ["view", "update"],
            "guest": ["view"]
        }
        return action in permissions.get(self.role, [])
    

class CrewRegistryProxy:
    def __init__(self, user):
        self.user = user
        self.registry = CrewRegistry()

    def add_crew_member(self, crew_member):
        if not self.user.has_permission("add"):
            raise PermissionError(f"User '{self.user.username}' does not have permission to add crew members.")
        self.registry.add_crew_member(crew_member)

    def remove_crew_member(self, crew_id):
        if not self.user.has_permission("remove"):
            raise PermissionError(f"User '{self.user.username}' does not have permission to remove crew members.")
        self.registry._crew_members.pop(crew_id, None)

    def get_crew_member(self, crew_id):
        if not self.user.has_permission("view"):
            raise PermissionError(f"User '{self.user.username}' does not have permission to view crew members.")
        return self.registry.get_crew_member(crew_id)

    def all_crew(self):
        if not self.user.has_permission("view"):
            raise PermissionError(f"User '{self.user.username}' does not have permission to view crew members.")
        return self.registry.all_crew()

    def update_crew_member_status(self, crew_id, status):
        if not self.user.has_permission("update"):
            raise PermissionError(f"User '{self.user.username}' does not have permission to update crew members.")
        member = self.registry.get_crew_member(crew_id)
        if member:
            member.update_status(status)
        else:
            raise ValueError(f"No crew member found with ID {crew_id}")

class CrewMember:
    def __init__(self, crew_id, name, role, contact_info):
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
        
        # Register this crew member
        CrewRegistry().add_crew_member(self)

    def assign_flight(self, flight_id):
        if not isinstance(flight_id, str):
            raise TypeError("Flight ID must be a string.")
        if self.status == "On Duty":
            raise Exception(f"{self.name} is already assigned to flight {self.assigned_flight}.")
            
        self.assigned_flight = flight_id
        self.status = "On Duty"

    def view_schedule(self):
        return self.assigned_flight or "No assigned flight."

    def update_status(self, new_status):
        valid_statuses = ["Available", "On Duty", "Resting", "Boarding Passengers"]
        if new_status not in valid_statuses:
            raise ValueError(f"'{new_status}' is not a valid status. Valid options are: {valid_statuses}")
            
        self.status = new_status

    def to_dict(self):
        return {
            "crew_id": self.crew_id,
            "name": self.name,
            "role": self.role,
            "contact_info": self.contact_info,
            "assigned_flight": self.assigned_flight,
            "status": self.status
        }