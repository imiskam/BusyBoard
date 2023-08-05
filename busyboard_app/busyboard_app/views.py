import datetime
import json
import random
from datetime import timezone, timedelta

from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .forms import *
from .models import *


def landing(request):
    """
    Renders the landing page of the BusyBoard application.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered landing page.
    """

    return render(request, 'busyboard_landing/index.html')


def contact_us(request):
    """
    Renders the contact us page of the BusyBoard application and handles the contact form submission.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered contact us page or a success message if the form is valid.
    """

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extract the cleaned data from the form
            name = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data.get('email')
            message = form.cleaned_data.get('message')

            # Send an email with the form data
            send_mail(
                'New Feedback',
                f'Name: {name}\nPhone: {phone}\nEmail: {email}\n\nMessage:\n{message}',
                'busyboard.feedback@gmail.com',
                ['busyboard@yopmail.com'],
                fail_silently=False,
            )

            # Render the contact us page with a success message
            return render(request, 'busyboard_landing/contact_us.html', {'message': 'Thanks for contacting us!'})

    else:
        # If the request method is not POST, create a new instance of the ContactForm
        form = ContactForm()

    # Render the contact us page with the form
    return render(request, 'busyboard_landing/contact_us.html', {'form': form})


def sign_up(request):
    """
    Renders the sign up page of the BusyBoard application and handles the user registration.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered sign up page or a redirect to the user's boards if registration is successful.
    """

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the user object created from the form
            user = form.save()

            # Log in the user
            login(request, user)

            # Redirect to the user's boards page
            return redirect('my_boards')
    else:
        # If the request method is not POST, create a new instance of the CustomUserCreationForm
        form = CustomUserCreationForm()

    # Render the sign up page with the form
    return render(request, 'busyboard_landing/sign_up.html', {'form': form})


def sign_in(request):
    """
    Renders the sign in page of the BusyBoard application and handles user authentication.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered sign in page or a redirect to the user's boards if authentication is successful.
    """

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Get the authenticated user object from the form
            user = form.get_user()

            # Log in the user
            login(request, user)

            # Redirect to the user's boards page
            return redirect('my_boards')
    else:
        # If the request method is not POST, create a new instance of the AuthenticationForm
        form = AuthenticationForm()

    # Render the sign in page with the form
    return render(request, 'busyboard_landing/sign_in.html', {'form': form})


def sign_out(request):
    """
    Logs out the user and redirects to the home page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect to the home page.
    """

    logout(request)
    return redirect('home')


@login_required(login_url='sign_in')
def settings(request):
    """
    Renders the settings page of the BusyBoard application and handles user profile updates, password changes, and account deletion.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered settings page or a redirect to various pages based on the action performed.
    """

    # Create an instance of the UserProfileUpdateForm with the current user's data
    user_profile_update_form = UserProfileUpdateForm(request.POST or None, instance=request.user)
    password_change_form = None

    if request.method == 'POST':
        # Check if the 'delete_photo' button was clicked
        if 'delete_photo' in request.POST:
            # Delete the user's profile photo
            request.user.profile_photo.delete(save=True)
            return redirect('settings')
        # Check if the 'change_photo' button was clicked
        elif 'change_photo' in request.POST:
            # Update the user's profile photo with the new photo
            request.user.profile_photo = request.FILES['new_photo']
            request.user.save()
            return redirect('settings')
        # Check if the 'delete_account' button was clicked
        elif 'delete_account' in request.POST:
            # Delete the user's account and log them out
            request.user.delete()
            logout(request)
            return redirect('home')
        # Check if the user profile update form is valid
        elif user_profile_update_form.is_valid():
            # Save the updated user profile data
            user_profile_update_form.save()
            return redirect('settings')
        # Check if the 'change_password' button was clicked
        elif 'change_password' in request.POST:
            # Create an instance of the PasswordChangeForm with the current user's data
            password_change_form = PasswordChangeForm(request.user, request.POST)
            if password_change_form.is_valid():
                # Save the updated password and update the session authentication hash
                user = password_change_form.save()
                update_session_auth_hash(request, user)
                return redirect('settings')
    else:
        # Create an instance of the PasswordChangeForm with the current user's data
        password_change_form = PasswordChangeForm(request.user)

    # Prepare the context data to be passed to the template
    context = {
        'user_profile_update_form': user_profile_update_form,
        'password_change_form': password_change_form,
    }

    # Render the settings page with the context data
    return render(request, 'busyboard_boards/settings.html', context)


@login_required(login_url='sign_in')
def my_boards(request):
    """
    Renders the "My Boards" page of the BusyBoard application, displaying the boards owned by the user and the boards they are invited to.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered "My Boards" page.
    """

    # Retrieve the boards owned by the user
    owned_boards = Board.objects.filter(owner=request.user)

    # Retrieve the boards the user is invited to
    invited_boards = Board.objects.filter(invited_users=request.user)

    # Prepare the context data to be passed to the template
    context = {
        'owned_boards': owned_boards,
        'invited_boards': invited_boards
    }

    # Render the "My Boards" page with the context data
    return render(request, 'busyboard_boards/my_boards.html', context)


@login_required(login_url='sign_in')
def create_board(request):
    """
    Handles the creation of a new board in the BusyBoard application.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect to the "My Boards" page after creating the board or a rendered "My Boards" page if the request method is GET.
    """

    if request.method == 'POST':
        # Retrieve the title and description from the form data
        title = request.POST.get('title')
        description = request.POST.get('description')

        # Generate a slug from the title
        slug = slugify(title)

        # Define a list of colors for the board
        colors = ['#4C5251', '#323232', '#034649', '#2B3C4A', '#494E13', '#544545', '#430405', '#250E2A', '#343B51',
                  '#1F4239', '#403E1C', '#2C1618', '#142E32', '#1B1B23']

        # Select a random color from the list
        color = random.choice(colors)

        # Create a new board object with the provided data
        board = Board(title=title, description=description, owner=request.user, slug=slug, color=color)

        # Save the board to the database
        board.save()

        # Redirect to the "My Boards" page
        return redirect('my_boards')
    else:
        # Retrieve the boards owned by the user
        boards = Board.objects.filter(owner=request.user)

        # Render the "My Boards" page with the boards data
        return render(request, 'busyboard_boards/my_boards.html', {'boards': boards})


@login_required(login_url='sign_in')
def edit_board(request, board_id):
    """
    Renders the board editing page and handles the update of board title and description.

    Args:
        request (HttpRequest): The HTTP request object.
        board_id (int): The ID of the board to be edited.

    Returns:
        HttpResponse: A redirect to the board editing page after saving the changes or a rendered board editing page.
    """

    # Retrieve the board object with the given board_id or return a 404 error if not found
    board = get_object_or_404(Board, id=board_id)

    if request.method == 'POST':
        # Retrieve the updated title and description from the form data
        title = request.POST.get('title')
        description = request.POST.get('description')

        # Update the board's title and description if provided
        if title:
            board.title = title
        if description:
            board.description = description

        # Save the changes to the board
        board.save()

        # Redirect to the board editing page
        return redirect('edit_board', board_id=board_id)

    # Render the board editing page with the board data
    return render(request, 'busyboard_boards/edit_board.html', {'board': board})


@login_required(login_url='sign_in')
def save_board_changes(request, board_id):
    """
    Saves the changes made to a board's title and description.

    Args:
        request (HttpRequest): The HTTP request object.
        board_id (int): The ID of the board to be edited.

    Returns:
        HttpResponse: A redirect to the "My Boards" page after saving the changes.
    """

    # Retrieve the board object with the given board_id or return a 404 error if not found
    board = get_object_or_404(Board, id=board_id)

    if request.method == 'POST':
        # Retrieve the updated title and description from the form data
        board.title = request.POST.get('title')
        board.description = request.POST.get('description')

        # Save the changes to the board
        board.save()

    # Redirect to the "My Boards" page
    return redirect('my_boards')


@login_required(login_url='sign_in')
def delete_board(request, board_id):
    """
    Deletes a board.

    Args:
        request (HttpRequest): The HTTP request object.
        board_id (int): The ID of the board to be deleted.

    Returns:
        HttpResponse: A redirect to the "My Boards" page after deleting the board.
    """

    if request.method == 'POST':
        # Retrieve the board object with the given board_id
        board = Board.objects.get(id=board_id)

        # Delete the board
        board.delete()

    # Redirect to the "My Boards" page
    return redirect('my_boards')


@login_required(login_url='sign_in')
def board_details(request, slug):
    """
    Renders the board details page of the BusyBoard application, displaying the cards, statistics and search results related to the board.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug of the board.

    Returns:
        HttpResponse: The rendered board details page or a forbidden response if the user does not have access to the board.
    """

    # Retrieve the board object with the given slug or return a 404 error if not found
    board = get_object_or_404(Board, slug=slug)

    # Retrieve the search query from the request GET parameters
    query = request.GET.get('search')

    # Get the current datetime
    now = datetime.datetime.now()

    # Count the number of cards with status 'DONE' updated today
    daily_done = Card.objects.filter(board=board, status='DONE', update_datetime__day=now.day).count()

    # Count the number of cards with status 'DONE' updated in the past 7 days
    weekly_done = Card.objects.filter(board=board, status='DONE', update_datetime__gte=now - timedelta(days=7)).count()

    # Count the number of cards with status 'DONE' updated in the past 30 days
    monthly_done = Card.objects.filter(board=board, status='DONE',
                                       update_datetime__gte=now - timedelta(days=30)).count()

    # Count the number of cards with status 'DONE' updated in the past 365 days
    annually_done = Card.objects.filter(board=board, status='DONE',
                                        update_datetime__gte=now - timedelta(days=365)).count()

    # Check if the user has access to the board
    if not (request.user == board.owner or request.user in board.users.all()):
        return HttpResponseForbidden("You do not have access to this board.")

    if query:
        # Filter cards by title and description based on the search query
        todo_cards = Card.objects.filter(
            Q(board=board, status='TO_DO', title__icontains=query) |
            Q(board=board, status='TO_DO', description__icontains=query)
        ).order_by('-create_datetime')

        in_progress_cards = Card.objects.filter(
            Q(board=board, status='IN_PROGRESS', title__icontains=query) |
            Q(board=board, status='IN_PROGRESS', description__icontains=query)
        ).order_by('-create_datetime')

        done_cards = Card.objects.filter(
            Q(board=board, status='DONE', title__icontains=query) |
            Q(board=board, status='DONE', description__icontains=query)
        ).order_by('-create_datetime')
    else:
        # Retrieve cards without search query
        todo_cards = Card.objects.filter(board=board, status='TO_DO').order_by('-create_datetime')
        in_progress_cards = Card.objects.filter(board=board, status='IN_PROGRESS').order_by('-create_datetime')
        done_cards = Card.objects.filter(board=board, status='DONE').order_by('-create_datetime')

    # Prepare the context data to be passed to the template
    context = {
        'board': board,
        'todo_cards': todo_cards,
        'in_progress_cards': in_progress_cards,
        'done_cards': done_cards,
        'daily_done': daily_done,
        'weekly_done': weekly_done,
        'monthly_done': monthly_done,
        'annually_done': annually_done,
    }

    # Render the board details page with the context data
    return render(request, 'busyboard_boards/board_details.html', context)


@login_required(login_url='sign_in')
def invite_to_board(request, slug):
    """
    Handles the invitation of a user to a board in the BusyBoard application.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug of the board.

    Returns:
        HttpResponse: A redirect to the board details page after inviting the user or a rendered invitations page if the request method is GET.
    """

    # Retrieve the board object with the given slug or return a 404 error if not found
    board = get_object_or_404(Board, slug=slug)

    if request.method == 'POST':
        # Retrieve the username of the user to invite from the form data
        username = request.POST['username']

        # Retrieve the user object with the given username or return a 404 error if not found
        user_to_invite = get_object_or_404(CustomUser, username=username)

        # Add the user to the invited_users list of the board
        board.invited_users.add(user_to_invite)

        # Add the board to the invited_boards list of the user
        user_to_invite.invited_boards.add(board)

        # Redirect to the board details page
        return redirect('board_details', slug=slug)

    # Render the invitations page with the board data
    return render(request, 'busyboard_boards/invitations.html', {'board': board})


@login_required(login_url='sign_in')
def remove_user_from_board(request, slug):
    """
    Removes a user from a board in the BusyBoard application.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug of the board.

    Returns:
        HttpResponse: A redirect to the "My Boards" page after removing the user from the board.
    """

    # Retrieve the board object with the given slug or return a 404 error if not found
    board = get_object_or_404(Board, slug=slug)

    if request.method == 'POST':
        # Retrieve the username of the user to remove from the form data
        username = request.POST['username']

        # Retrieve the user object with the given username or return a 404 error if not found
        user_to_remove = get_object_or_404(CustomUser, username=username)

        # Check if the request user is the owner of the board and the user to remove is in the invited_users list
        if request.user == board.owner and user_to_remove in board.invited_users.all():
            # Remove the user from the invited_users list of the board
            board.invited_users.remove(user_to_remove)

            # Remove the board from the invited_boards list of the user
            user_to_remove.invited_boards.remove(board)

    # Redirect to the "My Boards" page
    return redirect('my_boards')


@login_required(login_url='sign_in')
def leave_board(request, slug):
    """
    Allows a user to leave a board in the BusyBoard application.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug of the board.

    Returns:
        HttpResponse: A redirect to the "My Boards" page after leaving the board.
    """

    # Retrieve the board object with the given slug or return a 404 error if not found
    board = get_object_or_404(Board, slug=slug)

    if request.user in board.invited_users.all():
        # Remove the user from the invited_users list of the board
        board.invited_users.remove(request.user)

        # Remove the board from the invited_boards list of the user
        request.user.invited_boards.remove(board)

    return redirect('my_boards')


@login_required(login_url='sign_in')
@csrf_exempt
def create_card(request):
    """
    Handles the creation of a new card in the BusyBoard application.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect to the board details page after creating the card or a redirect to the board details page if the request method is not POST.
    """

    if request.method == 'POST':
        # Retrieve the board ID from the form data
        board_id = request.POST.get('board')

        # Retrieve the board object with the given ID or return a 404 error if not found
        board = get_object_or_404(Board, id=board_id)

        # Retrieve the card details from the form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        attachment = request.FILES.get('attachment')
        colors = ['#4C5251', '#323232', '#034649', '#2B3C4A', '#494E13', '#544545', '#430405', '#250E2A', '#343B51',
                  '#1F4239', '#403E1C', '#2C1618', '#142E32', '#1B1B23']

        # Select a random color from the list
        color = random.choice(colors)

        # Create a new card object with the provided data
        card = Card(title=title, description=description, priority=priority, attachment=attachment, board=board,
                    creator=request.user, color=color)

        # Save the card to the database
        card.save()

        # Redirect to the board details page
        return redirect('board_details', slug=board.slug)
    else:
        # Redirect to the board details page
        return redirect('board_details')


@login_required(login_url='sign_in')
@csrf_exempt
def update_card_status(request):
    """
    Updates the status of a card in the BusyBoard application.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response with the updated status if the request method is POST, or an error message if the request method is not POST.
    """

    if request.method == 'POST':
        # Retrieve the card ID and status from the form data
        card_id = request.POST.get('card_id')
        status = request.POST.get('status')

        # Retrieve the card object with the given ID
        card = Card.objects.get(id=card_id)

        # Update the status of the card
        card.status = status

        # Save the updated card to the database
        card.save()

        # Return a JSON response with the updated status
        return JsonResponse({'status': 'success', 'new_status': status})

    # Return a JSON response with an error message for invalid requests
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required(login_url='sign_in')
def get_card_details(request, card_id):
    """
    Retrieves the details of a card in the BusyBoard application.

    Args:
        request (HttpRequest): The HTTP request object.
        card_id (int): The ID of the card to retrieve details for.

    Returns:
        JsonResponse: A JSON response with the details of the card.
    """

    # Retrieve the card object with the given card_id from the database
    card = Card.objects.get(pk=card_id)

    # Get the username of the card's creator if it exists, otherwise set it to None
    creator = card.creator.username if card.creator else None

    # Create a dictionary containing the details of the card
    card_details = {
        'title': card.title,
        'description': card.description,
        'creator': creator,
        'priority': card.priority,
        'attachment': card.attachment.url if card.attachment else None,
        'create_datetime': card.create_datetime.strftime('%B %d, %Y, %I:%M %p'),
        'update_datetime': card.update_datetime.strftime('%B %d, %Y, %I:%M %p'),
    }

    # Return the card details as a JSON response
    return JsonResponse(card_details)


@login_required(login_url='sign_in')
def edit_card(request, card_id):
    """
    Edit the details of a card.

    Args:
        request (HttpRequest): The HTTP request object.
        card_id (int): The ID of the card to be edited.

    Returns:
        HttpResponse: The HTTP response object.
    """

    # Retrieve the card object with the given card_id from the database
    card = Card.objects.get(id=card_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # If it is a POST request, render the edit_card.html template
        # and pass the card object as a context variable
        return render(request, 'busyboard_boards/edit_card.html', {'card': card})


@login_required(login_url='sign_in')
def save_card_changes(request, card_id):
    """
    Save the changes made to a card.

    Args:
        request (HttpRequest): The HTTP request object.
        card_id (int): The ID of the card to be saved.

    Returns:
        HttpResponse: The HTTP response object.
    """

    # Retrieve the card object with the given card_id from the database
    card = Card.objects.get(id=card_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Update the card's title, description, and priority with the values from the request
        card.title = request.POST.get('title')
        card.description = request.POST.get('description')
        card.priority = request.POST.get('priority')

        # Check if the 'delete_attachment' key is present in the request POST data
        if 'delete_attachment' in request.POST:
            # If it is present, delete the card's attachment and render the edit_card.html template
            # passing the card object as a context variable
            card.attachment.delete()
            return render(request, 'busyboard_boards/edit_card.html', {'card': card})

        # Check if the 'change_attachment' key is present in the request POST data
        elif 'change_attachment' in request.POST:
            # If it is present, retrieve the new attachment file from the request
            # delete the card's current attachment, assign the new attachment to the card,
            # save the card, and render the edit_card.html template passing the card object as a context variable
            new_attachment = request.FILES.get('new_attachment')
            card.attachment.delete()
            card.attachment = new_attachment
            card.save()
            return render(request, 'busyboard_boards/edit_card.html', {'card': card})

        # Save the changes made to the card
        card.save()

    # Redirect the user to the 'board_details' view for the card's board
    return redirect('board_details', slug=card.board.slug)


@login_required(login_url='sign_in')
def delete_card(request, card_id):
    """
    Delete a card from the BusyBoard application.

    Args:
        request (HttpRequest): The HTTP request object.
        card_id (int): The ID of the card to be deleted.

    Returns:
        HttpResponse: A redirect to the board details page of the card's board.
    """

    # Check if the request method is POST
    if request.method == 'POST':
        # Retrieve the card object with the given card_id from the database
        card = Card.objects.get(id=card_id)

        # Delete the card from the database
        card.delete()

        # Redirect the user to the 'board_details' view for the card's board
        # by passing the board's slug as a parameter
        return redirect('board_details', slug=card.board.slug)


@login_required(login_url='sign_in')
def export_board_to_json(request, board_id):
    """
    Exports a board and its cards to a JSON file.

    Args:
        request (HttpRequest): The HTTP request object.
        board_id (int): The ID of the board to be exported.

    Returns:
        HttpResponse: A JSON file containing the board and its cards.
    """

    # Retrieve the board object with the given board_id from the database
    board = Board.objects.get(id=board_id)

    # Retrieve all the cards associated with the board
    cards = Card.objects.filter(board=board)

    # Create a dictionary to store the board and card data
    board_data = {
        'board': {
            'title': board.title,
            'description': board.description,
            'owner': board.owner.username,
            'slug': board.slug,
            'color': board.color
        },
        'cards': []
    }

    # Iterate over each card and add its data to the board_data dictionary
    for card in cards:
        card_data = {
            'title': card.title,
            'description': card.description,
            'status': card.get_status_display(),
            'color': card.color
        }
        board_data['cards'].append(card_data)

    # Convert the board_data dictionary to JSON format
    json_data = json.dumps(board_data, indent=4)

    # Create an HTTP response with the JSON data
    response = HttpResponse(json_data, content_type='application/json')

    # Set the Content-Disposition header to specify the filename of the JSON file
    response['Content-Disposition'] = f'attachment; filename="{board.slug}.json"'

    # Return the HTTP response
    return response
