from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Question, Answer
from .forms import QuestionForm, AnswerForm


def index(request):
	page = request.GET.get('page', '1')  # 페이지
	kw = request.GET.get('kw', '')  # 검색어
	question_list = Question.objects.order_by('-create_date')
	if kw:
		question_list = question_list.filter(
			Q(subject__icontains=kw) |  # 제목 검색
			Q(content__icontains=kw) |  # 내용 검색
			Q(answer__content__icontains=kw) |  # 답변 내용 검색
			Q(author__username__icontains=kw) |  # 질문 글쓴이 검색
			Q(answer__author__username__icontains=kw)  # 답변 글쓴이 검색
		).distinct()
	paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
	page_obj = paginator.get_page(page)
	context = {'question_list': page_obj, 'page': page, 'kw': kw}
	return render(request, 'SiteExer/question_list.html', context)


@login_required(login_url='common:login')
def question_create(request):
	if request.method == 'POST':
		form = QuestionForm(request.POST)
		if form.is_valid():
			question = form.save(commit=False)
			question.author = request.user  # author 속성에 로그인 계정 저장
			question.create_date = timezone.now()
			question.save()
			return redirect('SiteExer:index')
	else:
		form = QuestionForm()
	context = {'form': form}
	return render(request, 'SiteExer/question_form.html', context)


def detail(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	context = {'question': question}
	return render(request, 'SiteExer/question_detail.html', context)


@login_required(login_url='common:login')
def question_modify(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	if request.user != question.author:
		messages.error(request, '수정권한이 없습니다')
		return redirect('SiteExer:detail', question_id=question.id)
	if request.method == "POST":
		form = QuestionForm(request.POST, instance=question)
		if form.is_valid():
			question = form.save(commit=False)
			question.modify_date = timezone.now()  # 수정일시 저장
			question.save()
			return redirect('SiteExer:detail', question_id=question.id)
	else:
		form = QuestionForm(instance=question)
	context = {'form': form}
	return render(request, 'SiteExer/question_form.html', context)


@login_required(login_url='common:login')
def question_delete(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	if request.user != question.author:
		messages.error(request, '삭제권한이 없습니다')
		return redirect('SiteExer:detail', question_id=question.id)
	question.delete()
	return redirect('SiteExer:index')


@login_required(login_url='common:login')
def question_vote(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	if request.user == question.author:
		messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
	else:
		question.voter.add(request.user)
	return redirect('SiteExer:detail', question_id=question.id)


@login_required(login_url='common:login')
def answer_create(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	if request.method == "POST":
		form = AnswerForm(request.POST)
		if form.is_valid():
			answer = form.save(commit=False)
			answer.author = request.user  # author 속성에 로그인 계정 저장
			answer.create_date = timezone.now()
			answer.question = question
			answer.save()
			return redirect(f"{resolve_url('SiteExer:detail', question_id=question.id)}#answer_{answer.id}")
	else:
		form = AnswerForm()
	context = {'question': question, 'form': form}
	return render(request, 'SiteExer/question_detail.html', context)


@login_required(login_url='common:login')
def answer_modify(request, answer_id):
	answer = get_object_or_404(Answer, pk=answer_id)
	if request.user != answer.author:
		messages.error(request, '수정권한이 없습니다')
		return redirect('SiteExer:detail', question_id=answer.question.id)
	if request.method == "POST":
		form = AnswerForm(request.POST, instance=answer)
		if form.is_valid():
			answer = form.save(commit=False)
			answer.modify_date = timezone.now()
			answer.save()
			return redirect(f"{resolve_url('SiteExer:detail', question_id=answer.question.id)}#answer_{answer.id}")
	else:
		form = AnswerForm(instance=answer)
	context = {'answer': answer, 'form': form}
	return render(request, 'SiteExer/answer_form.html', context)


@login_required(login_url='common:login')
def answer_delete(request, answer_id):
	answer = get_object_or_404(Answer, pk=answer_id)
	if request.user != answer.author:
		messages.error(request, '삭제권한이 없습니다')
	else:
		answer.delete()
	return redirect('SiteExer:detail', question_id=answer.question.id)


@login_required(login_url='common:login')
def answer_vote(request, answer_id):
	answer = get_object_or_404(Answer, pk=answer_id)
	if request.user == answer.author:
		messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
	else:
		answer.voter.add(request.user)
	return redirect(f"{resolve_url('SiteExer:detail', question_id=answer.question.id)}#answer_{answer.id}")
