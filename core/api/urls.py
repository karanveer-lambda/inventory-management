from django.urls import path
from home.views import *
from home.procurementviews import *
urlpatterns = [
    path('login/',login),
    path('register/',register),
    path('makevendor/',MakeVendor),
    path('createdemand/',CreateDemand),
    path('procurement/',SelectVendor),
    path('authenticate/',authenticateMiddleware),
    path('myorders/',getMyOrders),
    path('demandsForProcurementTeams/',demandsForProcurementTeams),
    path('getvendors/',getVendors)
]
