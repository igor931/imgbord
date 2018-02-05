from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, \
								PageNotAnInteger

from django.views.generic import ListView

from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail

from taggit.models import Tag

def post_list(request):
	posts = Post.objects.filter(status='published')
	return render(request,
					'post/list.html',
					{'posts': posts})
def post_detail(request, year, month, day, post):
	post = get_object_or_404(Post, slug=post,
								   status='published',
								   publish__year=year,
								   publish__month=month,
								   publish__day=day)
	comments = post.comments.filter(active=True)
	if request.method == 'POST':
		comment_form = CommentForm(data=request.POST)
		if comment_form.is_valid():
			new_comment = comment_form.save(commit=False)
			new_comment.post = post
			new_comment.save()
	else:
		comment_form = CommentForm()		
	return render(request, 'post/detail.html', {'post': post,
												'comments': comments,
												'comment_form': comment_form})

def post_list(request, tag_slug=None):
	object_list = Post.objects.filter(status="published")
	tag = None
	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)
		object_list = object_list.filter(tags__in=[tag])

	paginator = Paginator(object_list, 3)
	page = request.GET.get('page')
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		posts = paginator.page(1)
	except EmptyPage:
		posts = paginator.page(paginator.num_pages)
	return render(request, 'post/list.html', {'page': page,
											  'posts': posts,
											  'tag': tag})

class PostListView(ListView):
	queryset = Post.objects.filter(status='published')
	context_object_name = 'posts'
	paginate_by = 3
	template_name = 'post/list.html'	

def post_share(request, post_id):
	post = get_object_or_404(Post, id=post_id, status='published')
	sent = False
	if request.method == 'POST':
		form = EmailPostForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			post_url = request.build_absolute_uri(
								post.get_absolute_url())
			subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title) 
			message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
			send_mail(subject, message, 'agent53347@mail.ru', [cd['to']])
			sent = True
	else:
		form = EmailPostForm()
	return render(request, 'post/share.html', {'post': post,
											  'form': form,
											  'sent': sent})