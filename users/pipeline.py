def set_student_role(backend, user, response, is_new=False, *args, **kwargs):
    """
    Google OAuth orqali kelgan YANGI foydalanuvchiga
    avtomatik 'student' roli beriladi.
    Mavjud foydalanuvchilar o'zgartirilmaydi.
    """
    if user and is_new:
        if not getattr(user, 'role', None):
            user.role = 'student'
            user.save(update_fields=['role'])
