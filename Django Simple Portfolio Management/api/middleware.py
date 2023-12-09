# class UpdateLastActivityMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         return self.get_response(request)

#     def process_view(self, request, view_func, view_args, view_kwargs):
#         assert hasattr(request, 'user')

#         # need to separately detect user when used middleware with JWT (else Anonymous User)
#         try:
#             auth_res = authentication.JWTAuthentication().authenticate(request)
#         except InvalidToken:
#             return JsonResponse({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

#         if auth_res:
#             request.user = auth_res[0]
        
#         # save last_activity on each authenticated request
#         if request.user.is_authenticated:
#             request.user.profile.last_activity = timezone.now()  # assigning last_activity
#             request.user.save()  # this triggers signal on User model saving
#             print(f'MIDDLEWARE saved last_activity for {request.user}')