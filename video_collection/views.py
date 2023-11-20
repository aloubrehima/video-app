from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower
from .forms import VideoForm, SearchForm
from .models import Video

def home(request):
    app_name = 'Discipline and motivation videos'
    return render(request, 'video_collection/home.html', {'app_name': app_name})

def add(request):

    if request.method == 'POST': # check to see if the request is POST
        new_video_form = VideoForm(request.POST) # Create videoform is method is POST
        if new_video_form.is_valid():
            try:
                new_video_form.save()
                return redirect('video_list')
                #messages.info(request, 'New video saved!')
            except ValidationError:
                messages.warning(request, 'Invalid Youtube URL')
            except IntegrityError: # for duplicate data
                messages.warning(request, 'You already added that video')
        
        messages.warning(request, 'Please check data entered.')
        return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})

    new_video_form = VideoForm()
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})


def video_list(request):

    search_form = SearchForm(request.GET)  # Build form form data user has sent to app

    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term']  # example: 'discipline' or else
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name'))

    else:
        search_form = SearchForm()
        videos = Video.objects.order_by(Lower('name'))

    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form})


def video_data(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    return render(request, 'video_collection/video_data.html', {'video': video})


def delete_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    video.delete()
    return redirect('video_list')  

