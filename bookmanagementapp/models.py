from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class BookModel(models.Model):
    isbn = models.CharField(max_length=13, primary_key=True)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)

    # @propertyによってon_loanが属性のように使用できる
    @property
    def on_loan(self):
        return self.loans.filter(returned_date__isnull=True).exists()

    def __str__(self):
        return f"{self.title} ({self.isbn})"

class LoanModel(models.Model):
    book = models.ForeignKey(BookModel, on_delete=models.PROTECT, related_name='loans')  # Djangoは自動的にBookModel側にloansという名前の逆参照マネージャを作る
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrowed_date = models.DateTimeField(auto_now_add=True)
    returned_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        b = timezone.localtime(self.borrowed_date).strftime('%Y-%m-%d') if self.borrowed_date else '-'
        r = timezone.localtime(self.returned_date).strftime('%Y-%m-%d') if self.returned_date else '未返却'
        return f"{self.book.title} → {self.user} (貸出日：{b} 返却日：{r})"

    # 同じ本 (book) について、返却されていない (returned_date IS NULL) レコードは同時に 1 件しか存在できない制約を課す
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['book'],
                condition=models.Q(returned_date__isnull=True),
                name='unique_active_loan_per_book'
            )
        ]