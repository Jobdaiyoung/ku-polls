import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59,
                                                   seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_question_with_future_pub_date(self):
        """
        is_published() return False for the question with future pub_date
        """
        time = timezone.now() + datetime.timedelta(seconds=10)
        future_question = Question(pub_date=time)
        self.assertFalse(future_question.is_published())

    def test_is_published_with_question_with_default_pub_date(self):
        """
        is_published() return True for the question with the default pub_date
        """
        time = timezone.now()
        default_question = Question(pub_date=time)
        self.assertTrue(default_question.is_published())

    def test_is_published_with_question_with_past_pub_date(self):
        """
        is_published() return True for the question with past pub_date
        """
        time = timezone.now() - datetime.timedelta(days=1)
        past_question = Question(pub_date=time)
        self.assertTrue(past_question.is_published())

    def test_can_vote_with_question_within_end_date(self):
        """
        can_vote() return True with for the question within end_date
        """
        pub_time = timezone.now() - datetime.timedelta(minutes=5)
        end_time = timezone.now() + datetime.timedelta(days=5)
        question = Question(pub_date=pub_time, end_date=end_time)
        self.assertTrue(question.can_vote())

    def test_can_vote_with_expired_question(self):
        """
        can_vote() return False with for the question that past end_date
        """
        pub_time = timezone.now() - datetime.timedelta(days=5)
        end_time = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_time, end_date=end_time)
        self.assertFalse(question.can_vote())

    def test_can_vote_with_unpublished_question(self):
        """
        can_vote() return False with for question whose end_date < pub_date
        """
        pub_time = timezone.now() - datetime.timedelta(days=1)
        end_time = timezone.now() - datetime.timedelta(days=5)
        question = Question(pub_date=pub_time, end_date=end_time)
        self.assertFalse(question.can_vote())

    def test_can_vote_with_no_pub_date_question(self):
        """
        can_vote() return True with for the question without end_date
        """
        pub_time = timezone.now() - datetime.timedelta(minutes=5)
        question = Question(pub_date=pub_time)
        self.assertTrue(question.can_vote())


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text='Future question.',
                                          days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.',
                                        days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
