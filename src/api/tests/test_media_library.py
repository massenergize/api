import json
from urllib.parse import urlencode
from django.test import TestCase, Client
from django.urls import reverse
from api.tests.common import (
    createImage,
    createUsers,
    makeAction,
    makeAdmin,
    makeCommunity,
    makeEvent,
    makeMedia,
    makeTestimonial,
    makeUser,
    makeUserUpload,
    signinAs,
)
from _main_.utils.utils import Console
from database.models import Media

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

    # def test_fetch(self):
    #     content = self.inflate_database()
    #     community1, community2, community3 = content.get("communities")
    #     route = self.routes.get("protected").get("fetch")
    #     Console.header("Test Fetching Images As Admin")
    #     for admin in [self.cadmin, self.sadmin]:
    #         data = {"community_ids": list([community1.id, community2.id, community3.id])}
    #         Console.log("Data", data)
    #         signinAs(self.client, admin)
    #         response = self.client.post(route, data)
    #         print(response.content)
    # to be continued!

    # def test_image_info(self):
    #     """
    #     Idea:
    #     Create an image record in the database
    #     Use the image to create one event, an action, and a testiomonial record in the db
    #     Run a request to retrieve information about the media record in the database
    #     The request should retrieve one event, one action, and one testimonial that match the  just
    #     created records.
    #     """
    #     media = makeMedia(name="Picture of my face")
    #     event = makeEvent(image=media)
    #     action = makeAction(image=media)
    #     story = makeTestimonial(image=media)
    #     community = makeCommunity(name="Lit Community")
    #     Console.underline("Testing image info")
    #     cadmin = makeAdmin(full_name="Pongo Admin", communities=[community])
    #     signinAs(self.client, cadmin)
    #     route = self.routes.get("protected").get("image-info")
    #     response = self.client.post(route, {"media_id": media.id})
    #     response = response.json()
    #     data = response.get("data").get("info")
    #     event_in_response = data.get("events")[0]
    #     action_in_response = data.get("actions")[0]
    #     story_in_response = data.get("testimonials")[0]
    #     event_is_good = event.name == event_in_response.get("name")
    #     action_is_good = action.title == action_in_response.get("title")
    #     story_is_good = story.title == story_in_response.get("title")
    #     if event_is_good:
    #         print("Media retrieved appropriate related events")
    #     self.assertTrue(event_is_good)

    #     if action_is_good:
    #         print("Media retrieved appropriate related actions")
    #     self.assertTrue(action_is_good)

    #     if story_is_good:
    #         print("Media retrieved appropriated related testimonials")
    #     self.assertTrue(story_is_good)

    def test_remove_image(self):
        """
        Idea:
        Create a media record in the database
        Send http request to remove image from database
        Expect an okay response
        Try to find the item in the db again,
        expect an empty response
        """
        media = makeMedia(name="Fake Media")
        signinAs(self.client, self.cadmin)
        if media:
            print(f"New media record '{media.name}' is created!")
        route = self.routes.get("protected").get("remove")
        response = self.client.post(route, {"media_id": media.id})
        response = response.json()
        ok_response = response.get("success")
        self.assertTrue(ok_response)
        try:
            Media.objects.get(id=media.id)
        except Media.DoesNotExist:
            print("Media has been removed successfully!")

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

        # actions = [
        #     makeAction(title="Action1", community=community1, image=media4),
        #     makeAction(title="Action2", community=community2, image=media5),
        #     makeAction(title="Action3", community=community3, image=media6),
        # ]

        # uploads = [
        #     makeUserUpload(media=media7, communities=[community1], user=user1),
        #     makeUserUpload(media=media8, communities=[community2], user=user2),
        #     makeUserUpload(media=media9, communities=[community3], user=user3),
        # ]
        Console.underline()

        return {
            # "actions": actions,
            "events": events,
            # "uploads": uploads,
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
