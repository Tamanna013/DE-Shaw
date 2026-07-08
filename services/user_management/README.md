# TestLens User Management Module

Provides RBAC, user profile management, and team assignments. Depends on the Auth module for verifying JWT tokens.

## Setup

```bash
pip install -r requirements.txt
uvicorn services.user_management.main:app --port 8001 --reload
```

## Roles

- Admin
- Engineering Manager
- Platform Engineer
- SDET
- Developer
- Read-Only

## Features
- Paginated user list with role and team filters
- Admins can assign roles. Last Admin cannot remove their own role.
- Team creation and member management.

## Integration Note
Deactivated users (`is_active=False`) are updated in `user_profiles`. The auth module should eventually check the profile repository during login to prevent deactivated users from obtaining new tokens.
