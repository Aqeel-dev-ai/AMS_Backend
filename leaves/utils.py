# leaves/utils.py
from rest_framework.exceptions import ValidationError

def update_leave_status(leave, new_status, comment=None, allowed_status='pending'):
    if leave.status != allowed_status:
        raise ValidationError(f"Cannot change status for a leave that is already '{leave.status}'")

    leave.status = new_status
    if comment:
        leave.admin_comment = comment
    leave.save()
    
    # If leave is approved, handle attendance records
    if new_status == 'approved':
        from attendance.services import handle_approved_leave
        handle_approved_leave(leave)
    
    return leave

