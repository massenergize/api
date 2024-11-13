from _main_.utils.utils import Console
from api.tests.common import createImage, createUsers, makeCommunity, makeUser, signinAs
from django.test import Client, TestCase


class CustomPagesIntegrationTestCase(TestCase):
    @staticmethod
    def setUpClass():
        pass

    def setUp(self):
        self.client = Client()
        self.USER, self.CADMIN, self.SADMIN = createUsers()
        self.user = makeUser()
        self.IMAGE = createImage(
            "https://www.whitehouse.gov/wp-content/uploads/2021/04/P20210303AS-1901-cropped.jpg"
        )
        self.COMMUNITY_1 = makeCommunity()
        self.COMMUNITY_2 = makeCommunity()
        self.COMMUNITY_3 = makeCommunity()

    @staticmethod
    def tearDownClass():
        pass

    def make_request(self, endpoint, data):
        return self.client.post(f'/api/{endpoint}', data=data, format='multipart').json()

    def test_create_community_custom_page(self):
        Console.header("Testing create custom menu: as super admin")
        
        signinAs(self.client, self.SADMIN)
        endpoint = "menus.create"
        args = {
            "title": "Test Title",
            "community_id": self.COMMUNITY_1.id,
            "content": [{
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
        },}},},}],}

        self.make_request('create_community_custom_page', args)