from multipledispatch import dispatch

class CrewRegistry:
    _instance = None
    _crew_members = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @dispatch(object)
    def add_crew_member(self, crew_member):
        self._crew_members[crew_member.crew_id] = crew_member
        
    @dispatch(dict)
    def add_crew_member(self, crew_data):
        if 'crew_id' not in crew_data:
            raise ValueError("crew_data must contain 'crew_id' key")
        self._crew_members[crew_data['crew_id']] = crew_data

    def get_crew_member(self, crew_id):
        return self._crew_members.get(crew_id)

    def all_crew(self):
        return list(self._crew_members.values())
    
    def __str__(self):
        return f"CrewRegistry with {len(self._crew_members)} crew members"
    
    @dispatch()
    def clear(self):
        self._crew_members.clear()
        
    @dispatch(int)
    def clear(self, crew_id):
        self._crew_members.pop(crew_id, None)

class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

    @dispatch(str)
    def has_permission(self, action):
        permissions = {
            "admin": ["add", "remove", "view", "update"],
            "staff": ["view", "update"],
            "guest": ["view"]
        }
        return action in permissions.get(self.role, [])
    
    @dispatch(list)
    def has_permission(self, actions):
        permissions = {
            "admin": ["add", "remove", "view", "update"],
            "staff": ["view", "update"],
            "guest": ["view"]
        }
        role_permissions = permissions.get(self.role, [])
        return all(action in role_permissions for action in actions)
            
    def __str__(self):
        return f"User(username='{self.username}', role='{self.role}')"

class CrewRegistryProxy:
    def __init__(self, user):
        self.user = user
        self.registry = CrewRegistry()

    @dispatch(object)
    def add_crew_member(self, crew_member):
        if not self.user.has_permission("add"):
            raise PermissionError(f"User '{self.user.username}' does not have permission to add crew members.")
        self.registry.add_crew_member(crew_member)
    
    @dispatch(dict)
    def add_crew_member(self, crew_data):
        if not self.user.has_permission("add"):
            raise PermissionError(f"User '{self.user.username}' does not have permission to add crew members.")
        self.registry.add_crew_member(crew_data)

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
    
    def __str__(self):
        return f"CrewRegistryProxy(user='{self.user.username}')"

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

    @dispatch(str)
    def assign_flight(self, flight_id):
        if self.status == "On Duty":
            raise Exception(f"{self.name} is already assigned to flight {self.assigned_flight}.")
            
        self.assigned_flight = flight_id
        self.status = "On Duty"
        
    @dispatch(dict)
    def assign_flight(self, flight_details):
        if 'id' not in flight_details:
            raise ValueError("flight_details must contain 'id' key")
            
        flight_id = flight_details['id']
        if not isinstance(flight_id, str):
            raise TypeError("Flight ID must be a string.")
            
        if self.status == "On Duty":
            raise Exception(f"{self.name} is already assigned to flight {self.assigned_flight}.")
            
        self.assigned_flight = flight_id
        self.status = "On Duty"
        
        if hasattr(self, 'flight_details'):
            self.flight_details = flight_details
        else:
            self.flight_details = flight_details

    def view_schedule(self):
        return self.assigned_flight or "No assigned flight."

    @dispatch(str)
    def update_status(self, new_status):
        valid_statuses = ["Available", "On Duty", "Resting", "Boarding Passengers"]
        if new_status not in valid_statuses:
            raise ValueError(f"'{new_status}' is not a valid status. Valid options are: {valid_statuses}")
            
        self.status = new_status
        
    @dispatch(str, dict)
    def update_status(self, new_status, details):
        valid_statuses = ["Available", "On Duty", "Resting", "Boarding Passengers"]
        if new_status not in valid_statuses:
            raise ValueError(f"'{new_status}' is not a valid status. Valid options are: {valid_statuses}")
            
        self.status = new_status
        self.status_details = details

    def to_dict(self):
        result = {
            "crew_id": self.crew_id,
            "name": self.name,
            "role": self.role,
            "contact_info": self.contact_info,
            "assigned_flight": self.assigned_flight,
            "status": self.status
        }
        
        if hasattr(self, 'status_details'):
            result["status_details"] = self.status_details
        if hasattr(self, 'flight_details'):
            result["flight_details"] = self.flight_details
            
        return result
    
    def __str__(self):
        return f"CrewMember(id={self.crew_id}, name='{self.name}', role='{self.role}', status='{self.status}')"
    
    def __eq__(self, other):
        if not isinstance(other, CrewMember):
            return False
        return self.crew_id == other.crew_id
