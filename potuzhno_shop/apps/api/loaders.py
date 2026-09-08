# from asgiref.sync import sync_to_async
# from graphene.utils.dataloader import DataLoader
# from django.contrib.auth.models import User
#
#
# class UserLoader(DataLoader):
#     async def batch_load_fn(self, keys):
#         users = await sync_to_async(list)(
#             User.objects.filter(id__in=keys)
#         )
#         by_id = {u.id: u for u in users}
#         return [by_id.get(k) for k in keys]