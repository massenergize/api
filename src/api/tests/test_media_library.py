from django.test import TestCase, Client
from django.urls import reverse
from api.tests.common import (
    createImage,
    createUsers,
    makeAction,
    makeCommunity,
    makeEvent,
    makeMedia,
    makeUser,
    makeUserUpload,
    signinAs,
)
from _main_.utils.utils import Console

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
        Console.header("Testing Media Library Now")
        self.user, self.cadmin, self.sadmin = createUsers()
        self.client = Client()
        self.routes = ROUTES
        self.users = {
            "Regular User": self.user,
            "Community Admin": self.cadmin,
            "Super Admin": self.sadmin,
        }

    # def test_block_normal_users(self):
    #     Console.underline()
    #     print("Normal users are not allowed in media library protected routes")
    #     Console.underline()
    #     protected_routes = self.routes.get("protected")
    #     for name, route in protected_routes.items():
    #         print(f"Regular user is not allowed to -> {name} ")
    #         response = self.client.post(route)
    #         error = response.json().get("error")
    #         self.assertEquals(error, "permission_denied")
    #     Console.underline("End test_block_normal_users")

    # def test_user_add_new_upload(self):
    #     Console.underline()
    #     print("Any user type is able to add new media")
    #     Console.underline()

    #     add = self.routes.get("add")
    #     for name, user in self.users.items():
    #         print(f"Uploading as --> {name}")
    #         signinAs(self.client, user)
    #         data = {
    #             "title": f"new {name} upload",
    #             "user_id": user.id,
    #             "file": createImage(),
    #         }

    #         response = self.client.post(add, data)
    #         status = response.status_code
    #         response = response.json()
    #         returned_user = response.get("data").get("user")
    #         passed = returned_user.get("full_name"), name

    #         self.assertEquals(status, 200)
    #         self.assertTrue(passed)
    #         if passed:
    #             print(f"{name} was able to add new upload to the library!")
    #     Console.underline("End test_user_add_new_upload")

    def test_fetch(self):
        content = self.inflate_database()
        community1, community2, community3 = content.get("communities")
        route = self.routes.get("protected").get("fetch")
        Console.header("Test Fetching Images As Admin")
        for admin in [self.cadmin, self.sadmin]:
            data = {"community_ids": [community1.id, community2.id, community3.id]}
            signinAs(self.client, admin)
            response = self.client.post(route, data)
            print(response.content)

    def inflate_database(self):
        Console.header(
            "Inflating database with communities, actions, events, media, and user media uploads"
        )

        community1, community2, community3 = [
            makeCommunity(subdomain="first"),
            makeCommunity(subdomain="second"),
            makeCommunity(subdomain="third"),
        ]
        user1, user2, user3 = [
            makeUser(email="mediauser1@gmail.com"),
            makeUser(email="mediauser2@gmail.com"),
            makeUser(email="mediauser3@gmail.com"),
        ]

        media1, media2, media3, media4, media5, media6, media7, media8, media9 = [
            makeMedia(name="media1"),
            makeMedia(name="media2"),
            makeMedia(name="media3"),
            makeMedia(name="media4"),
            makeMedia(name="media5"),
            makeMedia(name="media6"),
            makeMedia(name="media7"),
            makeMedia(name="media8"),
            makeMedia(name="media9"), 
        ]

        events = [
            makeEvent(name="First event", community=community1, image=media1),
            makeEvent(name="Second event", community=community2, image=media2),
            makeEvent(name="Third event", community=community3, image=media3),
        ]

        actions = [
            makeAction(title="Action1", community=community1, image=media4),
            makeAction(title="Action2", community=community2, image=media5),
            makeAction(title="Action3", community=community3, image=media6),
        ]

        uploads = [
            makeUserUpload(media=media7, communities=[community1], user=user1),
            makeUserUpload(media=media8, communities=[community2], user=user2),
            makeUserUpload(media=media9, communities=[community3], user=user3),
        ]
        Console.underline()

        return {
            "actions": actions,
            "events": events,
            "uploads": uploads,
            "communities": [community1, community2, community3],
            "users": [user1, user2, user3],
            "media": [
                media1,
                media2,
                media3,
                media4,
                media5,
                media6,
                media7,
                media8,
                media9,
            ],
        }
