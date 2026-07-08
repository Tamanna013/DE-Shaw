class DomainError(Exception):
    pass

class UnauthorizedError(DomainError):
    pass

class ResourceNotFoundError(DomainError):
    pass

class UserAlreadyInTeamError(DomainError):
    pass

class LastAdminRemovalError(DomainError):
    def __init__(self):
        super().__init__("Cannot remove the role of the last Admin in the organization.")

class TeamNotEmptyError(DomainError):
    def __init__(self, count: int):
        super().__init__(f"Team has {count} active members. Use force=true to delete.")
        self.count = count

class InvalidRoleError(DomainError):
    pass
