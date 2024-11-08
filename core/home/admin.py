from django.contrib import admin
from .models import Vendor,RegisterUser,Demand,Procurement
# Register your models here.
class CustomAdmin(admin.ModelAdmin):
    list_display = ('id',)  # This will add the `id` field to the list display for every model

    def get_list_display(self, request):
        """
        Modify the list_display to include the `id` field along with any other default fields
        """
        # Fetch the default fields from the model
        default_fields = super().get_list_display(request)
        # Add the 'id' field to the front of the list
        return ('id',) + default_fields
admin.site.register(Vendor,CustomAdmin)
admin.site.register(RegisterUser,CustomAdmin)
admin.site.register(Demand,CustomAdmin)
admin.site.register(Procurement,CustomAdmin)