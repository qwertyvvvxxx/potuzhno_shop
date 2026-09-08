# from types import SimpleNamespace
# from apps.api.loaders import UserLoader
#
# class LoadersMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         request.loaders = SimpleNamespace(user_by_id=UserLoader())
#         return self.get_response(request)