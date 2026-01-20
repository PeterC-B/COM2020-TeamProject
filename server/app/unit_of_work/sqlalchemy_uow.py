# Holds the single unit of work that manages transactions with the database
class SqlAlchemyUnitOfWork:
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self

    def commit(self):
        self.session.commit()

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.session.rollback()
        # let exceptions bubble
        return False
