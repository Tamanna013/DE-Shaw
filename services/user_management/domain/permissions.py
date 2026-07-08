from services.user_management.domain.roles import Role

# Mapping roles to granular permissions used across TestLens
ROLE_PERMISSIONS: dict[Role, list[str]] = {
    Role.ADMIN: [
        "can_manage_users",
        "can_configure_repo_integration",
        "can_view_analytics",
        "can_manage_teams",
        "can_write_tests",
    ],
    Role.ENGINEERING_MANAGER: [
        "can_view_analytics",
        "can_manage_teams",
    ],
    Role.PLATFORM_ENGINEER: [
        "can_configure_repo_integration",
        "can_view_analytics",
    ],
    Role.SDET: [
        "can_write_tests",
        "can_view_analytics",
    ],
    Role.DEVELOPER: [
        "can_write_tests",
        "can_view_analytics",
    ],
    Role.READ_ONLY: [
        "can_view_analytics",
    ]
}

def get_permissions_for_role(role: Role) -> list[str]:
    return ROLE_PERMISSIONS.get(role, [])
