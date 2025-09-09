from src.db import session


class BaseRepository:
    def __init__(self):
        self.db = session
