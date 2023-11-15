from django.test import TestCase
from django.urls import reverse
from .models import Video
from django.db import IntegrityError
from django.core.exceptions import ValidationError

class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Discipline and motivation videos app')


class TestAddVideos(TestCase):
    
    def test_add_video(self):

        valid_video = {
            'name': 'winner',
            'url': 'https://www.youtube.com/watch?v=U24wsr048FY',
            'notes': 'discipline your mind'
        }

        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)

        self.assertTemplateUsed('video_collection/video_list.html') # redirect to video list

        # video list => new video
        self.assertContains(response, 'discipline')
        self.assertContains(response, 'discipline your mind')
        self.assertContains(response, 'https://www.youtube.com/watch?v=U24wsr048FY')

        video_count = Video.objects.count()
        self.assertEqual(1, video_count) # only one video in the databse

        video = Video.objects.first() # if there's 1 video it should be the one added

        self.assertEqual('winner', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=U24wsr048FY', video.url)
        self.assertEqual('discipline your mind', video.notes)
        self.assertEqual('U24wsr048FY', video.video_id)

    def test_add_video_invalid_url_not_added(self):

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            'https://minneapolis.edu',
            'https://github.com/sjs'
        ]

        for invalid_video_url in invalid_video_urls: # looping through each invalid URL to test the adding functionality

            new_video = {
                'name': 'example',
                'url': invalid_video_url,
                'notes': 'example notes'
            }

            url = reverse('add_video')
            response = self.client.post(url, new_video)  # post the new data to the add-video view

            self.assertTemplateNotUsed('video_collection/add.html') # to make sure that the template was not used in response

            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]
            
            self.assertIn('Invalid Youtube URL', message_texts) # check is the message matches when the url is invalid
            self.assertIn('Please check data entered.', message_texts)

            video_count = Video.objects.count()  #  check that no new video was added
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):
    
    def test_all_videos_displayed_in_correct_order(self):
        v1 = Video.objects.create(name='BPE', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='hsx', notes='example', url='https://www.youtube.com/watch?v=656')
        v3 = Video.objects.create(name='BBB', notes='example', url='https://www.youtube.com/watch?v=849')
        v4 = Video.objects.create(name='clo', notes='example', url='https://www.youtube.com/watch?v=631')

        expected_video_order = [v3, v1, v4, v2]

        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_template = list(response.context['videos'])

        self.assertEqual(videos_in_template, expected_video_order)
    
    def test_no_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No videos')
        self.assertEquals(0, len(response.context['videos']))

    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='BPE', notes='example', url='https://www.youtube.com/watch?v=123')
        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='BPE', notes='example', url='https://www.youtube.com/watch?v=123')
        v1 = Video.objects.create(name='BPE', notes='example', url='https://www.youtube.com/watch?v=126')
        
        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '2 videos')
        

class TestVideoSearch(TestCase):
    
    def test_video_search_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)


    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = []  # empty list 
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No videos')


class TestVideoModel(TestCase):

    def test_invalid_urls_raise_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567'
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            '123456787654'
            'hhhhhhhhhhhhhhhhttps://www.youtube.com/watch'
            'http://www.youtube.com/watch/somethingelse?v=1234567'
            'https://minneapolis.edu',
            'https://github.com/sjs'
        ]

        for invalid_video_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='example', url=invalid_video_url, notes='example note')

        self.assertEqual(0, Video.objects.count())
    
    def duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='ABC', url='https://www.youtube.com/watch?v=456')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='ABC', url='https://www.youtube.com/watch?v=456')
        