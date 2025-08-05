from django.contrib import admin
from .models import BookModel, LoanModel
# Register your models here.

admin.site.register(BookModel)
admin.site.register(LoanModel)