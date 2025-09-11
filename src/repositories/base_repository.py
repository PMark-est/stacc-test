from sqlalchemy.orm import Session


class BaseRepository:
    """
    Minimal base repository storing a SQLAlchemy session.

    Concrete repositories should extend this for shared session access.
    """

    def __init__(self, session: Session) -> None:
        self.session: Session = session
