from django.test import TestCase
from _main_.utils.utils import Console
from api.store.common import find_duplicate_items
from api.tests.common import createImage, makeCommunity, makeMedia, makeUserUpload
from database.models import Media


# python manage.py test api.tests.test_find_duplicates_function.FindDuplicateItemsTest
class FindDuplicateItemsTest(TestCase):
    def setUp(self):
        """
        The function should only return image duplicates that are related to a specified list of communities!
        Meaning if one image has been duplicated about 4 times, but 2 of the duplicates belong to Wayland,
        and 2 belong to Framingham, when we look for duplicates in Wayland, it should only return that there
        are 2 duplicates of an image in Wayland.
        """
        # Create communities
        Console.header("Testing 'find_duplicates' function")
        print("Creating communities...")
        community1, community2, community3 = [
            makeCommunity(subdomain="first"),
            makeCommunity(subdomain="second"),
            makeCommunity(subdomain="third"),
        ]
        self.com1 = community1
        self.com2 = community2
        self.com3 = community3
        # Create some sample Media objects with duplicate hashes
        print("Generating media and linking to communities...")
        self.media1 = makeMedia(name="Biden")
        self.media2 = makeMedia(name="Biden")
        self.media3 = makeMedia(name="Biden")
        link = "https://www.massenergize.org/wp-content/uploads/2021/07/brad.png"
        image = createImage(link)
        self.media4 = makeMedia(name="Brad", image=image)
        self.media5 = makeMedia(name="Brad", image=createImage(link))
        self.media6 = makeMedia(name="Brad", image=createImage(link))
        self.mediapro = makeMedia(name="Media Pro")

        # upload1, upload2, upload3, upload4, upload5, upload6, pro

        uploads = [
            makeUserUpload(media=self.media1, communities=[community1]),
            makeUserUpload(media=self.media2, communities=[community1]),
            makeUserUpload(media=self.media4, communities=[community1]),
            # makeUserUpload(media=self.media4, communities=[community2]),
            makeUserUpload(media=self.media5, communities=[community2]),
            makeUserUpload(media=self.media6, communities=[community2]),
            makeUserUpload(media=self.mediapro, communities=[community3]),
        ]

    def test_find_duplicate_items(self):
        dupes_in_com1 = find_duplicate_items(False, community_ids=[self.com1.id])
        dupes_in_com2 = find_duplicate_items(False, community_ids=[self.com2.id])
        dupes_in_multiple_coms = find_duplicate_items(
            False, community_ids=[self.com1.id, self.com3.id]
        )

        dupes_in_com1 = list(dupes_in_com1.values())[0]
        dupes_in_com2 = list(dupes_in_com2.values())[0]
        dupes_in_multiple_coms = list(dupes_in_multiple_coms.values())[0]

        dupes_in_com1 = [m.id for m in dupes_in_com1]
        dupes_in_com2 = [m.id for m in dupes_in_com2]
        dupes_in_multiple_coms = [m.id for m in dupes_in_multiple_coms]

        self.assertEquals(len(dupes_in_com1), 2)
        self.assertIn(self.media1.id, dupes_in_com1)
        self.assertIn(self.media2.id, dupes_in_com1)
        self.assertEquals(len(dupes_in_com2), 2)
        self.assertIn(self.media5.id, dupes_in_com2)
        self.assertIn(self.media6.id, dupes_in_com2)
        self.assertEquals(len(dupes_in_multiple_coms), 3)
        self.assertIn(self.media1.id, dupes_in_multiple_coms)
        self.assertIn(self.media2.id, dupes_in_multiple_coms)
        self.assertIn(self.mediapro.id, dupes_in_multiple_coms)
        print("Identifying duplicates in specified communities works!")
