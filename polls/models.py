import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Represents a question that users can answer.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('end date', null=True, blank=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        """
        Checks if the question was published within the last day.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """
        Checks if the question is currently published.
        """
        now = timezone.now()
        return self.pub_date <= now

    def can_vote(self):
        """
        Checks if users can vote on the question.
        """
        now = timezone.now()
        if not self.is_published():
            return False
        if self.end_date is None:
            return True
        if self.pub_date <= now <= self.end_date:
            return True
        return False


class Choice(models.Model):
    """
    Represents a choice for a question that users can vote on.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)

    @property
    def votes(self):
        """
        count the vote for the Choice
        """
        # count = Vote.objects.filter(choice=self).count()
        return self.vote_set.count()

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    """
    Record a Vote of a Choice by a User.
    """
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
