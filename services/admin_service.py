from models import db
from models.user import User


def ensure_admin_user(admin_email=None):
    normalized_email = admin_email.strip().lower() if admin_email else None
    changed = False

    if normalized_email:
        user = User.query.filter_by(email=normalized_email).first()
        if user and not user.is_admin:
            user.is_admin = True
            changed = True
    elif User.query.count() > 0 and User.query.filter_by(is_admin=True).count() == 0:
        first_user = User.query.order_by(User.id.asc()).first()
        first_user.is_admin = True
        changed = True

    if changed:
        db.session.commit()
