from django.test import TestCase, Client
from django.urls import reverse
from api.tests.common import (
    createImage,
    createUsers,
    makeAction,
    makeCommunity,
    makeEvent,
    makeUser,
    signinAs,
)
from _main_.utils.utils import Console


"""
1. Create user, admin, sadmin 
2. Create multiple communities 
3. Create multiple events, actions, testimonials , userMedia Uploads
4. Create Media objects
5. Link all of them 
6. Then now test routes. How

"""
ROUTES = {
    "protected": {
        "fetch": "/api/gallery.fetch",
        "search": "/api/gallery.search",
        "image-info": "/api/gallery.image.info",
        "remove": "/api/gallery.remove",
    },
    "add": "/api/gallery.add",
}

# Run this particular test --> python manage.py test api.tests.test_media_library.TestMediaLibrary
class TestMediaLibrary(TestCase):
    def setUp(self) -> None:
        print("\n--------> Testing Media Library <----------\n")
        self.user, self.cadmin, self.sadmin = createUsers()
        self.client = Client()
        self.routes = ROUTES
        self.inflate_database()
        self.users = {
            "Regular User": self.user,
            "Community Admin": self.cadmin,
            "Super Admin": self.sadmin,
        }

    def test_block_normal_users(self):
        Console.underline()
        print("Normal users are not allowed in media library protected routes")
        Console.underline()
        protected_routes = self.routes.get("protected")
        for name, route in protected_routes.items():
            print(f"Regular user is not allowed to -> {name} ")
            response = self.client.post(route)
            error = response.json().get("error")
            self.assertEquals(error, "permission_denied")
        Console.underline("End test_block_normal_users")

    def test_user_add_new_upload(self):
        Console.underline()
        print("Any user type is able to add new media")
        Console.underline()
        
        add = self.routes.get("add")
        for name, user in self.users.items():
            print(f"Uploading as --> {name}")
            signinAs(self.client, user)
            data = {
                "title": f"new {name} upload",
                "user_id": user.id,
                "file": createImage(),
            }

            response = self.client.post(add, data)
            status = response.status_code
            response = response.json()
            returned_user = response.get("data").get("user")
            passed = returned_user.get("full_name"), name

            self.assertEquals(status, 200)
            self.assertTrue(passed)
            if passed:
                print(f"{name} was able to add new upload to the library!")
        Console.underline("End test_user_add_new_upload")

    @classmethod
    def inflate_database(self):
        """
        Create communities
        Assign users that manage the communities
        Create Events, TEstimonials & Actions that belong to the communities, with images
        Now create user media uploads with new users created

        """
        pass
