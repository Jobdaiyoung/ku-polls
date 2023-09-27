from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from .models import Question, Choice, Vote
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
            '-pub_date')


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
                           f"Poll number {kwargs['pk']} does not exists.")
            return redirect("polls:index")
        if not question.can_vote():
            messages.error(request,
                           f"Poll -{question.question_text}- is Already closed.")
            return redirect("polls:index")

        choice_selected = None
        if request.user.is_authenticated:
            try:
                vote = Vote.objects.get(user=request.user,
                                        choice__question=question)
                choice_selected = vote.choice
            except Vote.DoesNotExist:
                choice_selected = None
        return render(request, self.template_name, {"question": question,
                                                    "choice_selected":
                                                        choice_selected})


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
                           f"Poll number {kwargs['pk']} does not exists.")
            return redirect("polls:index")
        return render(request, self.template_name, {"question": question})


@login_required
def vote(request: HttpRequest, question_id: int) -> HttpResponse:
    """
    Function-based view for voting on a poll.
    """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        if question.can_vote():
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
            })
        else:
            messages.error(request,
                           f"Poll -{question.question_text}- is Already closed.")
            return redirect("polls:index")
    current_user = request.user
    try:
        # find a vote for this user and this question
        vote = Vote.objects.get(user=current_user, choice__question=question)
        # update his vote
        vote.choice = selected_choice
    except Vote.DoesNotExist:
        # no matching Vote - create new one
        vote = Vote(user=current_user, choice=selected_choice)

    vote.save()

    messages.success(request,
                     f"You have voted -({selected_choice})- for this poll.")
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
