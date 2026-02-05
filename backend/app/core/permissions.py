from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user


def require_role(role: str):
    def checker(user=Depends(get_current_user)):
        # Compare roles case-insensitively
        user_role = user.get("role") if isinstance(user, dict) else None
        if not user_role or user_role.upper() != str(role).upper():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden"
            )
        return user
    return checker
