from django.urls import path
#from .views import index, ping, actioninfo, eventinfo, groupinfo, stationinfo, eventsummary, userinfo, estimate, reset, importcsv, exportcsv, users, undo
from .views import index, actioninfo, estimate, importcsv, exportcsv, reset

urlpatterns = [
    path('',index),
    path('info',index),
    path('info/actions',index),
    path('info/action/<action>', actioninfo ),
    path('estimate/<action>', estimate ),
    path('import', importcsv ),
    path('export', exportcsv ),
    path('reset', reset)
]
