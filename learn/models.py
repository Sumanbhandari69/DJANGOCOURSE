from django.db import models
from django.contrib.auth.models import AbstractUser
import re
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from learn.managers import UserProfileManager
# Create your models here.

ARTICLE_STATUS = (
        ("draft", "draft"),
        ("in progress", "in progress"), 
        ("published", "published"),
        )

class UserProfile(AbstractUser):
    email = models.EmailField(_("email address"), max_length=255, unique=True)
    objects = UserProfileManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def article_count(self):
        return self.articles.count()
    
    @property
    def written_words(self):
        return self.articles.aggregate(models.Sum("word_count"))["word_count__sum"] or 0

class Article(models.Model):

    class Meta:
        verbose_name =_("Article")
        verbose_name_plural = _("Articles")
    title = models.CharField(_("title"), max_length=100)
    content =models.TextField(_("content"), blank=True, default="")
    word_count = models.IntegerField(_("word_count"), blank=True, default=0)
    twitter_post = models.TextField(_("twitter_post"), blank=True, default="")
    status = models.CharField(
        _("status"),
        max_length=20, 
        choices= ARTICLE_STATUS,
        default= "draft",
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name=_("creator"),
                                 on_delete=models.CASCADE,
                                 related_name= "articles"
                                 )

    def save(self, *args, **kwargs):
        text = re.sub(r"<[^>]*>", "", self.content).replace("&nbsp;", " ")
        self.word_count = len(re.findall(r"\b\w+\b", text))
        super().save(*args, **kwargs)
