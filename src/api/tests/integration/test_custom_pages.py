from _main_.utils.utils import Console
from api.tests.common import (
    createImage,
    createUsers,
    make_community_custom_page,
    makeCommunity,
    makeUser,
    signinAs,
)
from django.test import Client, TestCase

from database.utils.settings.model_constants.enums import SharingType


class CustomPagesIntegrationTestCase(TestCase):
    @staticmethod
    def setUpClass():
        pass

    def setUp(self):
        self.client = Client()
        self.USER, self.CADMIN, self.SADMIN = createUsers()
        self.user = makeUser()

        self.COMMUNITY_1 = makeCommunity()
        self.COMMUNITY_2 = makeCommunity()
        self.COMMUNITY_3 = makeCommunity()
        self.content = (
            [
                {
                    "block": {
                        "id": 1731409607781,
                        "name": "Paragraph",
                        "icon": "fa-paragraph",
                        "key": "paragraph",
                        "template": {
                            "element": {
                                "id": 1731409403366,
                                "type": "p",
                                "props": {
                                    "style": {"padding": 10, "margin": 0},
                                    "text": "Piano scales are one of the first things you learn as a beginner piano player, but why are they so important?  Well, playing your C major scale up and down isn’t just about practicing your technique; scales are a foundational musical concept. Understanding scales means you’ll understand key signatures and chords, which form the building blocks of Western music.  In this post, we’ll discuss why scales are important, break down the different types of scales, and show you ways to apply these scales to your piano playing.",
                                },
                            }
                        },
                    }
                }
            ],
        )

        self.p1, self.ccp1 = make_community_custom_page(
            title="Test Title 1",
            community=self.COMMUNITY_2,
            content=self.content,
        )
        self.p2, self.ccp2 = make_community_custom_page(
            title="Test Title 2",
            community=self.COMMUNITY_2,
            content=self.content,
        )

    @staticmethod
    def tearDownClass():
        pass

    def make_request(self, endpoint, data):
        return self.client.post(
            f"/api/{endpoint}", data=data, format="multipart"
        ).json()

    def test_create_community_custom_page(self):
        Console.header("Testing create custom page: as super admin")

        signinAs(self.client, self.SADMIN)
        endpoint = "community.custom.pages.create"
        args = {
            "title": "Test Title",
            "community_id": self.COMMUNITY_1.id,
            "content": [
                {
                    "options": {"position": 3},
                    "block": {
                        "id": 1731409607781,
                        "name": "Paragraph",
                        "icon": "fa-paragraph",
                        "key": "paragraph",
                        "template": {
                            "element": {
                                "id": 1731409403366,
                                "type": "p",
                                "props": {
                                    "style": {"padding": 10, "margin": 0},
                                    "text": "Piano scales are one of the first things you learn as a beginner piano player, but why are they so important?  Well, playing your C major scale up and down isn’t just about practicing your technique; scales are a foundational musical concept. Understanding scales means you’ll understand key signatures and chords, which form the building blocks of Western music.  In this post, we’ll discuss why scales are important, break down the different types of scales, and show you ways to apply these scales to your piano playing.",
                                },
                            }
                        },
                    },
                }
            ],
        }

        res = self.make_request(endpoint, args)

        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["page"]["title"], args["title"])
        self.assertIn("slug", res["data"]["page"])
        self.assertIn("content", res["data"]["page"])

        Console.header("Testing create custom page: as user")
        signinAs(self.client, self.user)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])

        Console.header("Testing create custom page: with missing title")
        args.pop("title")
        signinAs(self.client, self.SADMIN)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "You are Missing a Required Input: Title")

        Console.header("Testing create custom page: with missing community_id")
        args["title"] = "Test Title"
        args.pop("community_id")
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "You are Missing a Required Input: Community Id")

        Console.header("Testing create custom page: with invalid community_id")
        args["community_id"] = 000
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Community matching query does not exist.")

        Console.header("Testing create custom page: with audience and sharing_type")
        args["community_id"] = self.COMMUNITY_1.id
        args["audience"] = f"{self.COMMUNITY_2.id},{self.COMMUNITY_3.id}"
        args["sharing_type"] = SharingType.OPEN_TO.value[0]

        res = self.make_request(endpoint, args)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["sharing_type"], args["sharing_type"])
        audience = [c["id"] for c in res["data"]["audience"]]
        self.assertIn(self.COMMUNITY_2.id, audience)
        self.assertIn(self.COMMUNITY_3.id, audience)

    def test_update_community_custom_page(self):
        Console.header("Testing update custom page: as super admin")

        signinAs(self.client, self.SADMIN)
        endpoint = "community.custom.pages.update"

        args = {
            "id": self.p1.id,
            "title": "Test Title Updated",
            "slug": f"{self.COMMUNITY_2.subdomain}-test-title-updated",
            "content": [
                {
                    "options": {"position": 3},
                    "block": {
                        "id": 1731409607781,
                        "name": "Paragraph",
                        "icon": "fa-paragraph",
                        "key": "paragraph",
                        "template": {
                            "element": {
                                "id": 1731409403366,
                                "type": "p",
                                "props": {
                                    "style": {"padding": 10, "margin": 0},
                                    "text": "Piano scales are one of the first things you learn as a beginner piano player, but why are they so important?  Well, playing your C major scale up and down isn’t just about practicing your technique; scales are a foundational musical concept. Understanding scales means you’ll understand key signatures and chords, which form the building blocks of Western music.  In this post, we’ll discuss why scales are important, break down the different types of scales, and show you ways to apply these scales to your piano playing.",
                                },
                            }
                        },
                    },
                }
            ],
        }

        res = self.make_request(endpoint, args)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["page"]["title"], args["title"])
        self.assertEqual(res["data"]["page"]["slug"], args["slug"])

        Console.header("Testing update custom page: as user")
        signinAs(self.client, self.user)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])

        Console.header("Testing update custom page: with audience and sharing_type")
        args["audience"] = f"{self.COMMUNITY_1.id},{self.COMMUNITY_3.id}"
        args["sharing_type"] = SharingType.CLOSED_TO.value[0]

        signinAs(self.client, self.SADMIN)
        res = self.make_request(endpoint, args)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["sharing_type"], args["sharing_type"])
        audience = [c["id"] for c in res["data"]["audience"]]
        self.assertIn(self.COMMUNITY_1.id, audience)
        self.assertIn(self.COMMUNITY_3.id, audience)

        Console.header("Testing update custom page: with missing id")
        args.pop("id")
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "You are Missing a Required Input: Id")

        Console.header("Testing update custom page: with invalid id")
        args["id"] = "e13a5038-3dea-45ef-9dd1-00e4148a987d"
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "CustomPage matching query does not exist.")

    def test_delete_community_custom_page(self):
        Console.header("Testing delete custom page: as super admin")

        signinAs(self.client, self.SADMIN)
        endpoint = "community.custom.pages.delete"

        args = {
            "id": self.p1.id,
        }

        res = self.make_request(endpoint, args)
        self.assertTrue(res["success"])

        Console.header("Testing delete custom page: as user")
        signinAs(self.client, self.user)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])

        Console.header("Testing delete custom page: with missing id")
        args.pop("id")
        signinAs(self.client, self.SADMIN)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "You are Missing a Required Input: Id")

        Console.header("Testing delete custom page: with invalid id")
        args["id"] = "invalid-id"
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "['“invalid-id” is not a valid UUID.']")

    def test_community_custom_page_info(self):
        Console.header("Testing community custom page info: as super admin")

        signinAs(self.client, self.SADMIN)
        endpoint = "community.custom.pages.info"

        args = {"id": self.p1.id}

        res = self.make_request(endpoint, args)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["id"], str(self.p1.id))
        self.assertEqual(res["data"]["title"], self.p1.title)

        Console.header("Testing community custom page info: as user")
        signinAs(self.client, self.user)
        res = self.make_request(endpoint, args)
        self.assertTrue(res["success"])

        Console.header("Testing community custom page info: with missing id")
        args.pop("id")
        signinAs(self.client, self.SADMIN)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "You are Missing a Required Input: Id")

        Console.header("Testing community custom page info: with invalid id")
        args["id"] = "invalid-id"
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "['“invalid-id” is not a valid UUID.']")

    def test_share_community_custom_page(self):
        Console.header("Testing share custom page: as super admin")

        signinAs(self.client, self.SADMIN)
        endpoint = "community.custom.pages.share"

        args = {
            "community_page_id": self.ccp2.id,
            "community_ids": f"{self.COMMUNITY_1.id},{self.COMMUNITY_3.id}",
        }

        res = self.make_request(endpoint, args)
        self.assertTrue(res["success"])
        shared_communities = [c["id"] for c in res["data"]["shared_with"]]
        self.assertIn(self.COMMUNITY_1.id, shared_communities)
        self.assertIn(self.COMMUNITY_3.id, shared_communities)

        Console.header("Testing share custom page: as user")
        signinAs(self.client, self.user)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])

        Console.header("Testing share custom page: with missing community_page_id")
        args.pop("community_page_id")
        signinAs(self.client, self.SADMIN)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(
            res["error"], "You are Missing a Required Input: Community Page Id"
        )

        Console.header("Testing share custom page: with missing community_ids")
        args["community_page_id"] = self.p1.id
        args.pop("community_ids")
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(
            res["error"], "You are Missing a Required Input: Community Ids"
        )

        Console.header("Testing share custom page: with invalid community_page_id")
        args["community_page_id"] = "invalid-id"
        args["community_ids"] = [self.COMMUNITY_1.id, self.COMMUNITY_3.id]
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "['“invalid-id” is not a valid UUID.']")

        Console.header("Testing share custom page: with invalid community_ids")
        args["community_page_id"] = self.p1.id
        args["community_ids"] = ["invalid-id"]
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "CommunityCustomPage matching query does not exist.")

    def test_publish_custom_page(self):
        Console.header("Testing publish custom page: as super admin")

        signinAs(self.client, self.SADMIN)
        endpoint = "custom.page.publish"

        args = {"id": self.p1.id}

        res = self.make_request(endpoint, args)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["id"], str(self.p1.id))
        self.assertEqual(res["data"]["title"], self.p1.title)
        self.assertIsNotNone(res["data"]["latest_version"])

        Console.header("Testing publish custom page: as user")
        signinAs(self.client, self.user)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])

        Console.header("Testing publish custom page: with missing id")
        args.pop("id")
        signinAs(self.client, self.SADMIN)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "You are Missing a Required Input: Id")

        Console.header("Testing publish custom page: with invalid id")
        args["id"] = "invalid-id"
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "['“invalid-id” is not a valid UUID.']")

    def test_list_community_custom_pages(self):
        Console.header("Testing list community custom pages: as super admin")

        signinAs(self.client, self.SADMIN)
        endpoint = "community.custom.pages.list"

        args = {
            "community_id": self.COMMUNITY_1.id,
        }

        res = self.make_request(endpoint, args)
        self.assertTrue(res["success"])
        self.assertIsInstance(res["data"], list)

        Console.header("Testing list community custom pages: as user")
        signinAs(self.client, self.user)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])

        Console.header("Testing list community custom pages: with missing community_id")
        args.pop("community_id")
        signinAs(self.client, self.SADMIN)
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "You are Missing a Required Input: Community Id")

        Console.header("Testing list community custom pages: with invalid community_id")
        args["community_id"] = "invalid-id"
        res = self.make_request(endpoint, args)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Field 'id' expected a number but got 'invalid-id'.")
