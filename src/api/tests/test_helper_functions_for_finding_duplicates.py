from django.test import TestCase
from _main_.utils.utils import Console
from api.store.common import find_duplicate_items
from api.tests.common import createImage, makeAction, makeCommunity, makeEvent, makeHomePageSettings, makeMedia, makeTeam, makeUserUpload, makeVendor
from database.models import Media, Tag


# python manage.py test api.tests.test_helper_functions_for_finding_duplicates.TestHelperFunctionsForDuplicates
class TestHelperFunctionsForDuplicates(TestCase):
    # def setUp(self):
    #     pass

    def test_relationship_finder(self):
        Console.header("Testing Relationship Finder On Media Library")
        """
            The find_relationship function goes over all the relationships a media item has and retrieves all the items that use the particular media. 
            So if one media item is being used in 5 actions, 3 events, 10 community homepages, it will pull all of them and arrange all of them in groups as (actions, events, vendors, etc...)
            and return an object. 


            To test this, the idea is to: 

            Create a media object. 
            Create an action that uses it. 
            Create an event that uses it. 
            Create a vendor that uses it. 
            Create a team that uses it 
            Create a community and let it use it on it's homepage. 

            Then use the "find_relations_for_item" on the media object. 

            The function should return an object that has all the actions, events, teams etc 
            retrieved 
        """

       
        tag = Tag.objects.create(name = "Personal Tag")
        media = makeMedia(tags = [tag])
        com = makeCommunity(name="Top Community", logo=media)
        action = makeAction(image=media)
        event = makeEvent(image=media)
        team = makeTeam (logo=media, community =com )
        vendor = makeVendor(image=media)
        homepage = makeHomePageSettings(title="Top Settings", images = [media])
        

        
