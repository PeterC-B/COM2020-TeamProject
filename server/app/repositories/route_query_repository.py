from app.models.route_query_model import RouteQuery
from app.models.user_account_model import UserAccountModel

class RouteQueryRepository:
    def __init__(self, session):
        self.session = session

    def add(self, query: RouteQuery):
        self.session.add(query)

    def list_all(self):
        return (
            self.session.query(RouteQuery, UserAccountModel)
            .join(UserAccountModel, RouteQuery.user_id == UserAccountModel.user_id)
            .order_by(RouteQuery.timestamp.desc())
            .all()
        )
