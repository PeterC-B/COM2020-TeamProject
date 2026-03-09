from server.app.models.route_query_model import RouteQuery

class LogRouteQuery:
    def __init__(self, uow, repo):
        self.uow = uow
        self.repo = repo

    def execute(self, user_id, start, end, weights_json, chosen_route_rank, chosen_route_path):
        query = RouteQuery(
            user_id=user_id,
            start=start,
            end=end,
            weights_json=weights_json,
            chosen_route_rank=chosen_route_rank,
            chosen_route_path=chosen_route_path,
        )

        self.repo.add(query)
        self.uow.commit()
        return query
