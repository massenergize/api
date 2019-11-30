from django.urls import path
from .views import index, ping, actioninfo, eventinfo, groupinfo, stationinfo, estimate, reset, importcsv, exportcsv, users, userinfo

urlpatterns = [
    path('',index),
    path('info',index),
    path('info/actions',index),
    path('info/action/<action>', actioninfo ),
    path('info/events', eventinfo ),
    path('info/event/<event>', eventinfo ),
    path('info/groups', groupinfo ),
    path('info/group/<group>', groupinfo ),
    path('info/stations', stationinfo ),
    path('info/station/<station>', stationinfo ),
    path('info/users', userinfo ),
    path('info/user/<user>', userinfo ),
    path('estimate/<action>', estimate ),
    path('reset', reset ),
    path('import', importcsv ),
    path('export', exportcsv ),
    path('users', users)

]