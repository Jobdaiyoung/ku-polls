from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from .models import Question, Choice
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect


class IndexView(generic.ListView):
    """
    View for listing the latest polls.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by(
            '-pub_date')[:5]


class DetailView(generic.DetailView):
    """
    View for viewing the details of a poll.
    """
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, **kwargs):
        """Handle GET requests in detailView"""
        try:
            question = get_object_or_404(Question, pk=kwargs["pk"])
        except Http404:
            messages.error(request,
                           f"Poll number {kwargs['pk']} does not exists.")
            return redirect("polls:index")
        if not question.is_published():
            messages.error(request,
                           f"Poll number {question.id} Already closed.")
            return redirect("polls:index")
        return render(request, self.template_name, {"question": question})


class ResultsView(generic.DetailView):
    """
    View for displaying the results of a poll.
    """
    model = Question
    template_name = 'polls/results.html'

    def get(self, request, *args, **kwargs):
        """
        Handel the Get request for the ResultsView.
        """
        try:
            question = get_object_or_404(Question, pk=kwargs["pk"])
        except Http404:
            messages.error(request,
                           f"Poll number {kwargs['pk']} does not exists.")
            return redirect("polls:index")
        if not question.is_published():
            messages.error(request,
                           f"Poll number {question.id} Already closed.")
            return redirect("polls:index")
        return render(request, self.template_name, {"question": question})


def vote(request: HttpRequest, question_id: int) -> HttpResponse:
    """
    Function-based view for voting on a poll.
    """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))