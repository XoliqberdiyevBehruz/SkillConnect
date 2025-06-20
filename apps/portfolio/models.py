from django.db import models

from apps.shared.models import BaseModel
from apps.accounts.models import User


class Portfolio(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="porfolios")
    title = models.CharField(max_length=250)
    description = models.TextField()
    image = models.ImageField(upload_to='apps/portfoli/portfoli/image/')
    link = models.URLField()
    likes_count = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.title
    

class PortfoliLike(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolio_likes", db_index=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="portfolio_likes", db_index=True)
    
    class Meta:
        unique_together = ('user', 'portfolio')