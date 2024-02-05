import json
from urllib.parse import quote_plus, urlencode
from django.test import TestCase, Client
from django.urls import reverse
from api.tests.common import (
    createImage,
    createUsers,
    image_url_to_base64,
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
from database.models import Media, Tag

ROUTES = {
    "protected": {
        "fetch": "/api/gallery.fetch",
        "search": "/api/gallery.search",
        "image-info": "/api/gallery.image.info",
        "remove": "/api/gallery.remove",
        "edit": "/api/gallery.item.edit",
    },
    "add": "/api/gallery.add",
}


# Run this particular test --> python manage.py test api.tests.test_media_library.TestMediaLibrary
class TestMediaLibrary(TestCase):

    # @classmethod
    # def setUpTestData(cls) -> None:
    #     Console.header("Testing Media Library Now")
    #     cls.user, cls.cadmin, cls.sadmin = createUsers()
    #     cls.client = Client()
    #     cls.routes = ROUTES
    #     cls.users = {
    #         "Regular User": cls.user,
    #         "Community Admin": cls.cadmin,
    #         "Super Admin": cls.sadmin,
    #     }
    #     cls.DB = cls.inflate_database(cls)

    # def test_image_reading(self):
    """
    #         Procedure: 

    #         Upload an image
    #         Using the id of the media record created, 
    #         hit the route. 

    #         now get the base64 string of the image that was just uploaded manually,
    #         And match that string against the string that was returned from the route.
    #         If the results match, the route works well!
    # =================== NOTE: This test is not working ====================
     => The following test is commented out because it attempts to retrieve file references from the S3 bucket.
        During local testing, we don't have access to the S3 bucket, so this test will be re-enabled when access is available.
        Commenting out to prevent issues related to the unavailable S3 bucket in the local testing environment.
        Uncomment this test when access to the S3 bucket is established.

    """
    #     Console.underline("Testing Image Reading Route")
    #     print("Creating new media with new upload...")
    #     media = makeMedia() 
    #     base64 = image_url_to_base64() 
    #     print("Manually generating base64 of same uploaded media...")
    #     response = self.client.post("/api/gallery.image.read", data = {"media_id":media.id}).json() 
    #     base64_from_route = response.get("data")
    #     print("Checking if returned strings match...")
    #     self.assertFalse(base64_from_route == None)
    #     self.assertEqual(base64,base64_from_route)
    #     print("Route reads the right image and returns base64!")

    # def test_mine_and_user_specific_search(self):
    #     print("Signing in as cadmin")
    #     signinAs(self.client, self.cadmin)

    #     print("Uploading an image with signed in user details...")
    #     user_media_upload = makeUserUpload(user=self.cadmin)

    #     search_route = self.routes.get("protected").get("search")
    #     print("Running request to fetch images uploaded by signed in user...")
    #     response = self.client.post(search_route, data={"my_uploads": True}).json()
    #     data = response.get("data")
    #     count = data.get("count")
    #     self.assertEqual(count, 1)  # Only one image must be retrieved
    #     print("Checking if image response is the same as what was uploaded...")
    #     image_from_response = data.get("images")[0]
    #     self.assertEqual(
    #         user_media_upload.media.id, image_from_response.get("id")
    #     )  # And the image retrieved needs to be exactly the same one that was uploaded
    #     print("My upload retrieval works nicely!")

    #     # User specific
    #     Console.underline("Checking user spefic content")
    #     users = self.DB.get("users")
    #     print("Running a request with an array of a random user...")
    #     response = self.client.post(
    #         search_route, data={"user_ids": [users[2].id]}
    #     ).json()
    #     print("Checking if user retrieved images belong to the specified user...")
    #     data = response.get("data")
    #     count = data.get("count")

    #     self.assertEqual(count, 1)
    #     images = data.get("images")
    #     images = [im.get("id") for im in images]
    #     self.assertEqual(images[0], 9)

    #     print("User specific search brings in images by specified user ID nicely!")

    # def make_tags(self, words):
    #     tags = []
    #     for w in words:
    #         t = Tag.objects.create(name=w)
    #         tags.append(t)
    #     return tags

    # def test_keyword_search(self):
    #     signinAs(self.client, self.cadmin)
    #     search_route = self.routes.get("protected").get("search")
    #     words = ["one", "two", "three"]
    #     words_set_two = ["mass", "energize"]

    #     tags = self.make_tags(words)
    #     tags_set_two = self.make_tags(words_set_two)
    #     media =makeMedia(tags=tags)
    #     media2 = makeMedia(tags=tags_set_two)
    #     makeUserUpload(user=self.cadmin, media = media)
    #     makeUserUpload(user=self.cadmin, media = media2)

    #     response = self.client.post(search_route, data = {"keywords":words})
    #     data = response.json().get("data")
    #     response_image = data.get("images")[0]
    #     count = data.get("count")
    #     self.assertEqual(count,1)
    #     self.assertEqual(media.id, response_image.get("id"))

    # def test_search_by_community(self):
    #     Console.underline("Testing search by community")
    #     print("Signing in as admin")
    #     signinAs(self.client, self.cadmin)
    #     coms = self.DB.get("communities")
    #     com3 = coms[2]
    #     coms = [c.id for c in coms]
    #     search_route = self.routes.get("protected").get("search")
    #     print("Sending request with specific community ids...")
    #     response = self.client.post(
    #         search_route,
    #         data={"target_communities": [com3.id]},
    #     ).json()
    #     data = response.get("data")
    #     count = data.get("count")

    #     print("Checking if only images related to communities were retrieved...")

    #     self.assertEqual(count, 4)
    #     images = [im.get("id") for im in data.get("images")]
    #     self.assertEqual(
    #         set(images), set([3, 6, 9, 10])
    #     )  # if you check "inflate_db" you should see that community3 is related to medias with the listed IDs

    #     print("Search by community works well!")

    # def test_image_details_edit(self):
    #     Console.underline("Testing image details edit")
    #     coms = self.DB.get("communities")
    #     edit_route = self.routes.get("protected").get("edit")
    #     user_upload = makeUserUpload(user=self.cadmin)

    #     signinAs(self.client, self.cadmin)
    #     data = {
    #         "media_id": user_upload.media.id,
    #         "user_upload_id": user_upload.id,
    #         "copyright": True,
    #         "underAge": True,
    #         "guardian_info": "kidsmum@gmail.com",
    #         "copyright_att": "mrowner@gmail.com",
    #         "community_ids": [coms[0].id],
    #     }
    #     print("Sending request to update image details...")
    #     response = self.client.post(edit_route, data=data)
    #     response_data = response.json().get("data")
    #     # Console.log("RESPONSE", data)
    #     response_info = response_data.get("information").get("info")
    #     print("Checking if response matches details sent...")
    #     self.assertEqual(data["copyright"], response_info["has_copyright_permission"])
    #     self.assertEqual(data["copyright_att"], response_info["copyright_att"])
    #     self.assertEqual(data["underAge"], response_info["has_children"])
    #     self.assertEqual(data["guardian_info"], response_info["guardian_info"])

    #     communities = response_data.get("information").get("communities", [])
    #     self.assertEqual(coms[0].id, communities[0].get("id"))
    #     print("Editing works nicely!")

    # def test_image_info(self):
    #     """
    #     Idea:
    #     Create an image record in the database
    #     Use the image to create one event, an action, and a testiomonial record in the db
    #     Run a request to retrieve information about the media record in the database
    #     The request should retrieve one event, one action, and one testimonial that match the  just
    #     created records.
    #     """
    #     Console.header("Testing Image Info Retrieval")
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
    #     data = response.get("data").get("relations")
    #     event_in_response = data.get("event")[0]
    #     action_in_response = data.get("action")[0]
    #     story_in_response = data.get("testimonial")[0]
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

    # def test_remove_image(self):
    #     """
    #     Idea:
    #     Create a media record in the database
    #     Send http request to remove image from database
    #     Expect an okay response
    #     Try to find the item in the db again,
    #     expect an empty response
    #     """
    #     Console.header("Testing Media Removal As Admin")
    #     media = makeMedia(name="Fake Media")
    #     signinAs(self.client, self.cadmin)
    #     if media:
    #         print(f"New media record '{media.name}' is created!")
    #     route = self.routes.get("protected").get("remove")
    #     response = self.client.post(route, {"media_id": media.id})
    #     response = response.json()
    #     ok_response = response.get("success")
    #     self.assertTrue(ok_response)
    #     try:
    #         Media.objects.get(id=media.id)
    #     except Media.DoesNotExist:
    #         print("Media has been removed successfully!")

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
