from django.shortcuts import render

# Create your views here.

from catalog.models import Author, Book, BookInstance, Genre, Language

def index(request):
	"""View function for home page of the site."""

	#Generate the counts of some of the main objects.
	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()

	# Count of the Available books with status 'a'
	num_instances_available = BookInstance.objects.filter(status__exact='a').count()

	#The all is implied by default.
	num_authors = Author.objects.count()
	num_genres = Genre.objects.count()
	num_books_the = Book.objects.filter(title__icontains='the').count()

	# Number of visits to the view, as counted in the session variable
	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1

	context = {
		'num_books': num_books,
		'num_instances': num_instances,
		'num_instances_available': num_instances_available,
		'num_authors': num_authors,
		'num_genres': num_genres,
		'num_books_the': num_books_the,
		'num_visits': num_visits,
	}

	#Render the html template index.html with the data in the context variable
	return render(request, 'index.html', context=context)

from django.views import generic

class BookListView(generic.ListView):
	model = Book 
	paginate_by = 3

class BookDetailView(generic.DetailView):
	model = Book

class AuthorListView(generic.ListView):
	model = Author
	paginate_by = 10

class AuthorDetailView(generic.DetailView):
	model = Author

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
	"""Generic class-based view listing books on loans to a current user."""
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

from django.contrib.auth.mixins import PermissionRequiredMixin

class LoanedBooksForStaffListView(PermissionRequiredMixin,generic.ListView):
	"""Generic class-based views listing all the books that were borrowed by various users."""
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_books.html'
	paginate_by = 10
	permission_required = 'catalog.can_mark_returned'

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')


import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
	"""View function for renewing a specific bookinstance by librarian."""
	book_instance = get_object_or_404(BookInstance, pk=pk)

	# If this is a POSt request then process the Form data
	if request.method == 'POST':
		# Create a form instance and populate it with data from the request (binding):
		form = RenewBookForm(request.POST)

		# Check if the form is valid:
		if form.is_valid():
			# Process the data in form.cleaned_data as required (here we just write it to the model due_back field)
			book_instance.due_back = form.cleaned_data['renewal_date']
			book_instance.save()

			# redirect to a new url:
			return HttpResponseRedirect(reverse('loan-books'))

	# If this is the Get (or any other method) create the default form.
	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

	context = {
		'form': form,
		'book_instance': book_instance,
	}		

	return render(request, 'catalog/book_renew_librarian.html', context)
	

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

class AuthorCreate(PermissionRequiredMixin,CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin,UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin,DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Book

class BookCreate(PermissionRequiredMixin,CreateView):
	model = Book
	fields = '__all__'
	permission_required = 'catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin,UpdateView):
	model = Book
	fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
	permission_required = 'catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin,DeleteView):
	model = Book
	success_url = reverse_lazy('books')
	permission_required = 'catalog.can_mark_returned'




	