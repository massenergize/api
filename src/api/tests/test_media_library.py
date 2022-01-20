from django.test import TestCase, Client
from django.urls import reverse
from api.tests.common import createImage, createUsers, signinAs
from _main_.utils.utils import Console

"""
1. Create user, admin, sadmin 
2. Create multiple communities 
3. Create multiple events, actions, testimonials , userMedia Uploads
4. Create Media objects
5. Link all of them 
6. Then now test routes. How

"""


# Run this particular test --> python manage.py test api.tests.test_media_library.TestMediaLibrary
class TestMediaLibrary(TestCase):
    def setUp(self) -> None:
        print("\n--------> Testing Media Library <----------\n")
        self.user, self.cadmin, self.sadmin = createUsers()
        self.users = {
            "Normal User": self.user,
            "Community Admin": self.cadmin,
            "Super Admin": self.sadmin,
        }
        self.client = Client()
        self.routes = {
            "protected": {
                "fetch": "/api/gallery.fetch",
                "search": "/api/gallery.search",
                "image-info": "/api/gallery.image.info",
                "remove": "/api/gallery.remove",
            },
            "add": "/api/gallery.add",
        }

    def test_block_normal_users(self):
        print("Normal users are not allowed in media library protected routes")
        protected_routes = self.routes.get("protected")
        for name, route in protected_routes.items():
            print(f"Normal user is not allowed to -> {name} ")
            response = self.client.post(route)
            error = response.json().get("error")
            self.assertEquals(error, "permission_denied")
        print("-----------------------END test_block_normal_users ------------")

    def test_user_add_new_upload(self):
        print("Any user type is able to add new media")
        add = self.routes.get("add")
        for name, user in self.users.items():
            print(f"Uploading as --> {name}")
            signinAs(self.client, user)
            data = {
                "title": f"new {name} upload",
                "user_id": user.id,
                "file": createImage(),
            }
            response = self.client.post(add, data).json()
            Console.log(f"Response For {name}", response)
        # next, you have to check and see if the response came back with no errors,  
        # and now go and run the same query in post man, look at an example of a positive result , and map it to what it should look like in the test