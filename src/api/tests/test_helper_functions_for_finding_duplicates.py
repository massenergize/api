from django.test import TestCase
from _main_.utils.utils import Console
from api.store.common import (
    do_deletion,
    find_duplicate_items,
    find_relations_for_item,
    group_disposable,
)
from api.tests.common import (
    createImage,
    makeAction,
    makeCommunity,
    makeEvent,
    makeHomePageSettings,
    makeMedia,
    makeTeam,
    makeUserUpload,
    makeVendor,
)
from database.models import Media, Tag


# python manage.py test api.tests.test_helper_functions_for_finding_duplicates.TestHelperFunctionsForDuplicates
class TestHelperFunctionsForDuplicates(TestCase):
    # def setUp(self):
    #     pass

    # def test_relationship_finder(self):
    #     Console.header("Testing Relationship Finder On Media Library")
    #     """
    #         The find_relationship function goes over all the relationships a media item has and retrieves all the items that use the particular media.
    #         So if one media item is being used in 5 actions, 3 events, 10 community homepages, it will pull all of them and arrange all of them in groups as (actions, events, vendors, etc...)
    #         and return an object.

    #         To test this, the idea is to:

    #         Create a media object.
    #         Create an action that uses it.
    #         Create an event that uses it.
    #         Create a vendor that uses it.
    #         Create a team that uses it
    #         Create a community and let it use it on it's homepage.

    #         Then use the "find_relations_for_item" on the media object.

    #         The function should return an object that has all the actions, events, teams etc
    #         retrieved
    #     """

    #     tag = Tag.objects.create(name="Personal Tag")
    #     media = makeMedia(tags=[tag])
    #     com = makeCommunity(name="Top Community", logo=media)
    #     action = makeAction(image=media)
    #     event = makeEvent(image=media)
    #     team = makeTeam(logo=media, community=com)
    #     vendor = makeVendor(image=media)
    #     homepage = makeHomePageSettings(title="Top Settings", images=[media])

    #     item = find_relations_for_item(media)
    #     actions = item.get("actions", [])
    #     actions = [a.id for a in actions]
    #     com_logos = item.get("community_logos")
    #     com_logos = [com.id for com in com_logos]
    #     homepages = item.get("homepage", [])
    #     homepages = [h.id for h in homepages]
    #     teams = item.get("teams", [])
    #     teams = [t.id for t in teams]
    #     events = item.get("events", [])
    #     events = [e.id for e in events]
    #     vendors = item.get("vendors", [])
    #     vendors = [v.id for v in vendors]
    #     print("Checking to see if all related items are available...")
    #     self.assertEquals(len(actions), 1)
    #     self.assertIn(action.id, actions)
    #     self.assertEquals(len(com_logos), 1)
    #     self.assertIn(com.id, com_logos)
    #     self.assertEquals(len(homepages), 1)
    #     self.assertIn(homepage.id, homepages)
    #     self.assertEquals(len(teams), 1)
    #     self.assertIn(team.id, teams)
    #     self.assertEquals(len(events), 1)
    #     self.assertIn(event.id, events)
    #     self.assertEquals(len(vendors), 1)
    #     self.assertIn(vendor.id, vendors)
    #     print(
    #         "Actions, homepages, events, vendors, community logos,  all relations with media were retrieved successfully!"
    #     )

    def test_grouping_disposables_(self):
        """
        The idea is to create 3 media records with the same image and details.
        Then upload a 4th one, that is the same image, but with a different file name.

        Then pass the images through the group_disposable function.

        It should identify the 3 images as having the same s3 reference, and mark the 4th image as one with a different reference in the s3

        This means that when we have identified image duplicates, we will successfully be able to differentiate
        which items are simply duplicates because they have the same reference in the bucket,
        and which items are actual duplicates and with different file reference in the s3 bucket.

        """
        Console.header("Testing 'Group Disposables'")
        print("Creating media records...")
        media1 = makeMedia(filename="samsies")
        media2 = makeMedia(filename="samsies")
        media3 = makeMedia(filename="samsies")
        file = createImage(
            "https://www.whitehouse.gov/wp-content/uploads/2021/04/P20210303AS-1901-cropped.jpg"
        )
        different = makeMedia(file=file, filename="a-very-unique-name")

        print("Passing records down to be grouped...")
        disposable = [media2.id, media3.id, different.id]
        # disposable =  [m.id for m in disposable]
        has_same_ref, has_different_ref = group_disposable(
            media1.simple_json(), disposable
        )

        has_same_ref = [m.id for m in has_same_ref]
        has_different_ref = [m.id for m in has_different_ref]
        
        print("Checking to see if items were separated into the right groups...")
        self.assertEquals(len(has_same_ref), 2)
        self.assertIn(media2.id, has_same_ref)
        self.assertIn(media3.id, has_same_ref)

        self.assertEquals(len(has_different_ref), 1)
        self.assertIn(different.id, has_different_ref)
        print(
            "Awesome! Function was able to identify items with same reference, and items with different s3 bucket references!"
        )

        Console.header("Testing 'Do Deletion' Function")

        do_deletion(media1.simple_json(), disposable)

        items_in_there = Media.objects.filter(id__in=disposable)
        print("Trying to see if disposed items are removed...")
        self.assertEquals(len(items_in_there), 0)

        found_original = Media.objects.filter(id=media1.id).first()

        self.assertEquals(found_original.id, media1.id)

        print("Great! Disposables were removed, and original/primary image remained!")
