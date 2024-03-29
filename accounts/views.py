from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.selectors import get_accounts


class AccountsListView(APIView):

    def get(self, request: Request):
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        accounts = get_accounts(limit=limit + 1, offset=offset)
        is_end_of_list_reached = len(accounts) < limit + 1
        accounts = [
            {
                'name': account.name,
                'login': account.login,
                'password': account.password,
                'roles': [
                    {
                        'id': role.id,
                        'name': role.name,
                    } for role in account.roles.all()
                ],
            } for account in accounts[:limit]
        ]
        response_data = {
            'accounts': accounts,
            'is_end_of_list_reached': is_end_of_list_reached,
        }
        return Response(response_data)
