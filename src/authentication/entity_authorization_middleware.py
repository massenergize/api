"""
Middle ware for authorization for users before they access specific resources
"""
from _main_.utils.massenergize_errors import NotAuthorizedError, CustomMassenergizeError
from _main_.utils.context import Context
from api import services

class EntityAuthorizationMiddleware:

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    # Code to be executed for each request before
    # the view (and later middleware) are called.

    response = self.get_response(request)

    # Code to be executed for each request/response after
    # the view is called.

    return response


  def process_view(self, request, view_func, *view_args, **view_kwargs):

    try:
      route = request.path


      # whitelisted routes
      if request.path in set([
        '/ping',
        '/auth.logout',
        '/auth.logout',

      ]):
        # it is not a protected route so let them through
        return


      # if we get there then this route is protected and we need to check
      # if the use has the right permissions
      # =================================================================

      # extract the context
      ctx: Context = request.context
      if not ctx.user_is_logged_in:
        raise NotAuthorizedError()
      

      if route in set([

      ]):
        return services.action.check_access(ctx, )
      elif route in set([ ]):
        return

    except Exception as e:
      return CustomMassenergizeError(e)

