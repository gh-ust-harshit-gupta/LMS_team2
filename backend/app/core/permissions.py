from fastapi import Depends, HTTPException, status
from app.controllers.auth_controller import get_current_user

def require_role(role: str):
    def checker(user=Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden"
            )
        return user
    return checker
