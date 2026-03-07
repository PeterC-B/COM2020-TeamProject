from server.app.models.route_query_model import RouteQuery

class RouteQueryRepository:
    def __init__(self, session):
        self.session = session

    def add(self, query: RouteQuery):
        self.session.add(query)

    def list_all(self):
        return (
            self.session.query(RouteQuery)
            .order_by(RouteQuery.timestamp.desc())
            .all()
        )
