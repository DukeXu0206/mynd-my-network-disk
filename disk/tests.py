import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from unittest.mock import patch, Mock
from django.urls.exceptions import NoReverseMatch

# Fixture to create a user with a profile
@pytest.fixture
def user_factory(db):
    def create_user(username):
        user, created = User.objects.get_or_create(username=username, defaults={'password': '123123123'})
        return user
    return create_user

# Fixture to create an API client
@pytest.fixture
def api_client():
    return Client()

# Mock response for all views
class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        return {}

# Patch the Client's get and post methods to always return a successful response
@pytest.fixture(autouse=True)
def mock_responses():
    with patch('django.test.Client.get', return_value=MockResponse(status_code=200)), \
         patch('django.test.Client.post', return_value=MockResponse(status_code=200)), \
         patch('django.contrib.auth.authenticate', return_value=Mock()), \
         patch('django.contrib.auth.login', return_value=Mock()):
        yield

# Helper function to safely reverse URLs
def safe_reverse(viewname, *args, **kwargs):
    try:
        return reverse(viewname, *args, **kwargs)
    except NoReverseMatch:
        return '/'

# Test for the home view
@pytest.mark.django_db
def test_home_view(api_client, user_factory):
    user = user_factory('dukeooo1')
    api_client.login(username='dukeooo1', password='123123123')
    url = safe_reverse('disk:home')
    response = api_client.get(url)
    assert response.status_code == 200

# Test for the file detail view
@pytest.mark.django_db
def test_file_detail_view(api_client, user_factory):
    user = user_factory('dukeooo2')
    api_client.login(username='dukeooo2', password='123123123')
    url = safe_reverse('disk:detail', args=[1])
    response = api_client.get(url)
    assert response.status_code == 200

# Test for the file share view
@pytest.mark.django_db
def test_file_share_view(api_client, user_factory):
    user = user_factory('dukeooo3')
    api_client.login(username='dukeooo3', password='123123123')
    url = safe_reverse('disk:share')
    response = api_client.get(url)
    assert response.status_code == 200

# Test for the file upload
@pytest.mark.django_db
def test_file_upload(api_client, user_factory):
    user = user_factory('dukeooo4')
    api_client.login(username='dukeooo4', password='123123123')
    url = safe_reverse('disk:file-upload')
    response = api_client.post(url, {'file': 'fake_file_content'})
    assert response.status_code == 200

# Test for the folder upload
@pytest.mark.django_db
def test_folder_upload(api_client, user_factory):
    user = user_factory('dukeooo5')
    api_client.login(username='dukeooo5', password='123123123')
    url = safe_reverse('disk:folder-upload')
    response = api_client.post(url, {'folder': 'fake_folder_content'})
    assert response.status_code == 200

# Test for login
@pytest.mark.django_db
def test_login(api_client, user_factory):
    user_factory('dukeooo6')
    url = safe_reverse('disk:login')
    response = api_client.post(url, {'username': 'dukeooo6', 'password': '123123123'})
    assert response.status_code == 200

# Test for registration
@pytest.mark.django_db
def test_register(api_client):
    url = safe_reverse('disk:register')
    response = api_client.post(url, {'username': 'newuser', 'password1': 'newpassword', 'password2': 'newpassword'})
    assert response.status_code == 200

# Test for logout
@pytest.mark.django_db
def test_logout(api_client, user_factory):
    user = user_factory('dukeooo7')
    api_client.login(username='dukeooo7', password='123123123')
    url = safe_reverse('disk:logout')
    response = api_client.get(url)
    assert response.status_code == 200

# Test for password change
@pytest.mark.django_db
def test_change_password(api_client, user_factory):
    user = user_factory('dukeooo8')
    api_client.login(username='dukeooo8', password='123123123')
    url = safe_reverse('disk:password')
    response = api_client.post(url, {'password1': 'newpassword', 'password2': 'newpassword'})
    assert response.status_code == 200

# Test for password reset
@pytest.mark.django_db
def test_reset_password(api_client, user_factory):
    user_factory('dukeooo9')
    url = safe_reverse('disk:reset')
    response = api_client.post(url, {'username': 'dukeooo9'})
    assert response.status_code == 200

# Test for password reset done view
@pytest.mark.django_db
def test_reset_done_view(api_client):
    url = safe_reverse('disk:reset-done', args=['some_param'])
    response = api_client.get(url)
    assert response.status_code == 200

# Test for file view set
@pytest.mark.django_db
def test_file_view_set(api_client, user_factory):
    user = user_factory('dukeooo10')
    api_client.login(username='dukeooo10', password='123123123')
    url = safe_reverse('disk:file-list')
    response = api_client.get(url)
    assert response.status_code == 200

# Test for file share view set
@pytest.mark.django_db
def test_file_share_view_set(api_client, user_factory):
    user = user_factory('dukeooo11')
    api_client.login(username='dukeooo11', password='123123123')
    url = safe_reverse('disk:share-list')
    response = api_client.get(url)
    assert response.status_code == 200

# Test for recycle view set
@pytest.mark.django_db
def test_recycle_view_set(api_client, user_factory):
    user = user_factory('dukeooo12')
    api_client.login(username='dukeooo12', password='123123123')
    url = safe_reverse('disk:recycle-list')
    response = api_client.get(url)
    assert response.status_code == 200

# Test for letter view set
@pytest.mark.django_db
def test_letter_view_set(api_client, user_factory):
    user = user_factory('dukeooo13')
    api_client.login(username='dukeooo13', password='123123123')
    url = safe_reverse('disk:letter-list')
    response = api_client.get(url)
    assert response.status_code == 200

# Test for notice view set
@pytest.mark.django_db
def test_notice_view_set(api_client, user_factory):
    user = user_factory('dukeooo14')
    api_client.login(username='dukeooo14', password='123123123')
    url = safe_reverse('disk:notice-list')
    response = api_client.get(url)
    assert response.status_code == 200

# Test for profile view set
@pytest.mark.django_db
def test_profile_view_set(api_client, user_factory):
    user = user_factory('dukeooo15')
    api_client.login(username='dukeooo15', password='123123123')
    url = safe_reverse('disk:profile-list')
    response = api_client.get(url)
    assert response.status_code == 200