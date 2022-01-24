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
    @classmethod
    def setUpTestData(cls) -> None:
        Console.header("Testing Media Library Now")
        cls.user, cls.cadmin, cls.sadmin = createUsers()
        cls.client = Client()
        cls.routes = ROUTES
        cls.users = {
            "Regular User": cls.user,
            "Community Admin": cls.cadmin,
            "Super Admin": cls.sadmin,
        }
        cls.DB = cls.inflate_database(cls)

    def test_block_normal_users(self):
        Console.header("Testing That Media Library Routes Are Protected")
        protected_routes = self.routes.get("protected")
        for name, route in protected_routes.items():
            print(f"Regular user is not allowed to -> {name} ")
            response = self.client.post(route)
            error = response.json().get("error")
            self.assertEquals(error, "permission_denied")
        Console.underline("End test_block_normal_users")

    def test_user_add_new_upload(self):
        Console.header("Testing That Any User Type Is Able To Add Media")
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

    def test_fetch_with_communities(self):
        """
        Idea:
        Create a few media records
        Create a few community records
        Use communities and media records to create events, actions, and testimonials
        Now run a request to retrieve images that belong to particular communities
        Go through response and see if the community object on each of the images presented
        is right
        """
        Console.header("Testing Community Specific Fetches")
        content = self.DB
        communities = content.get("communities")
        route = self.routes.get("protected").get("fetch")
        Console.header("Test Fetching Images As Admin")
        signinAs(self.client, self.cadmin)
        data = {"community_ids": list([communities[0].id])}
        response = self.client.post(route, data).json()
        images = response.get("data").get("images")
        valid_ids = [1, 4, 7, 10]
        valid = True  # True means all images is from the right community
        for image in images:
            if image.get("id") not in valid_ids:
                valid = False
                print(
                    "Some images in the response do not belong to the specified community...!"
                )
        self.assertTrue(valid)
        print("All images are from the specified community!")

    def test_search(self):
        """
        Idea:
        Sign in as admin
        Create different media records
        use records to create events, stories, testimonials and usermedia upload objects
        Now send a request to retrieve images related to filters provided
        Check if the returned images are only related to the filters provided

        """
        Console.header("Testing Search With Filters")
        content = self.DB
        communities = content.get("communities")
        filters = ["events"]
        signinAs(self.client, self.cadmin)
        route = self.routes.get("protected").get("search")
        data = {"target_communities": [communities[0].id], "filters": filters}
        response = self.client.post(route, data).json()
        images = response.get("data").get("images")
        event_ids = [1, 10]
        valid = True
        for img in images:
            if img.get("id") not in event_ids:
                valid = False
        self.assertTrue(valid)
        self.assertTrue(len(images) == 2)
        if valid:
            print(
                "Search only retrieved images that were related to events when the 'events' filter was set!"
            )

        data["filters"] = ["actions"]
        response = self.client.post(route, data).json()
        images = response.get("data").get("images")
        valid = True
        for img in images:
            action_image = content.get("actions")[0].simple_json().get("image")
            if img.get("id") != action_image.get("id"):
                valid = False
        self.assertTrue(valid)
        self.assertTrue(len(images) == 1)
        if valid:
            print(
                "Search only retrieved images that were related to actions when the 'actions' filter was set!"
            )

    def test_image_info(self):
        """
        Idea:
        Create an image record in the database
        Use the image to create one event, an action, and a testiomonial record in the db
        Run a request to retrieve information about the media record in the database
        The request should retrieve one event, one action, and one testimonial that match the  just
        created records.
        """
        Console.header("Testing Image Info Retrieval")
        media = makeMedia(name="Picture of my face")
        event = makeEvent(image=media)
        action = makeAction(image=media)
        story = makeTestimonial(image=media)
        community = makeCommunity(name="Lit Community")
        Console.underline("Testing image info")
        cadmin = makeAdmin(full_name="Pongo Admin", communities=[community])
        signinAs(self.client, cadmin)
        route = self.routes.get("protected").get("image-info")
        response = self.client.post(route, {"media_id": media.id})
        response = response.json()
        data = response.get("data").get("info")
        event_in_response = data.get("events")[0]
        action_in_response = data.get("actions")[0]
        story_in_response = data.get("testimonials")[0]
        event_is_good = event.name == event_in_response.get("name")
        action_is_good = action.title == action_in_response.get("title")
        story_is_good = story.title == story_in_response.get("title")
        if event_is_good:
            print("Media retrieved appropriate related events")
        self.assertTrue(event_is_good)

        if action_is_good:
            print("Media retrieved appropriate related actions")
        self.assertTrue(action_is_good)

        if story_is_good:
            print("Media retrieved appropriated related testimonials")
        self.assertTrue(story_is_good)

    def test_remove_image(self):
        """
        Idea:
        Create a media record in the database
        Send http request to remove image from database
        Expect an okay response
        Try to find the item in the db again,
        expect an empty response
        """
        Console.header("Testing Media Removal As Admin")
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

        (
            media1,
            media2,
            media3,
            media4,
            media5,
            media6,
            media7,
            media8,
            media9,
            media10,
        ) = [
            makeMedia(name="media1"),
            makeMedia(name="media2"),
            makeMedia(name="media3"),
            makeMedia(name="media4"),
            makeMedia(name="media5"),
            makeMedia(name="media6"),
            makeMedia(name="media7"),
            makeMedia(name="media8"),
            makeMedia(name="media9"),
            makeMedia(name="media10"),
        ]

        events = [
            makeEvent(name="First event", community=community1, image=media1),
            makeEvent(name="Second event", community=community2, image=media2),
            makeEvent(name="Third event", community=community3, image=media3),
            makeEvent(name="Fourth event", community=community1, image=media10),
        ]

        actions = [
            makeAction(title="Action1", community=community1, image=media4),
            makeAction(title="Action2", community=community2, image=media5),
            makeAction(title="Action3", community=community3, image=media6),
            makeAction(title="Action4", community=community3, image=media10),
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
