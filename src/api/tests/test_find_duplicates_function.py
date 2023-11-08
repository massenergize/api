from django.test import TestCase
from _main_.utils.utils import Console
from api.store.common import find_duplicate_items
from api.tests.common import createImage, makeCommunity, makeMedia, makeUserUpload

from database.models import Media


# python manage.py test api.tests.test_find_duplicates_function.FindDuplicateItemsTest
class FindDuplicateItemsTest(TestCase):
    def setUp(self):
        # Create communities
        community1, community2, community3 = [
            makeCommunity(subdomain="first"),
            makeCommunity(subdomain="second"),
            makeCommunity(subdomain="third"),
        ]
        self.com1 = community1
        self.com2 = community2
        self.com3 = community3

        # Create some sample Media objects with duplicate hashes
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
        # Call the find_duplicate_items function
        set1 = find_duplicate_items(
            False, community_ids=[self.com2.id]
        )  # Should find me dupes here
        # set2 = find_duplicate_items(False,community_ids=[self.com2.id])  # Should not find any dupes here
        # Console.log("SET 1",set1)
        # Console.log("SET 2",set1)
        Console.underline("SET 1")
        print("SET 1", set1)

        # print("SET 2", set2)

    # def tearDown(self):
    #     # Clean up by deleting the created Media objects
    #     self.media1.delete()
    #     self.media2.delete()
    #     self.media3.delete()
