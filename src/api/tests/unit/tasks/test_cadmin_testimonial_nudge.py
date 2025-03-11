from django.test.testcases import TestCase
from _main_.utils.feature_flag_keys import TESTIMONIAL_AUTO_SHARE_SETTINGS_NUDGE_FEATURE_FLAG_KEY
from _main_.utils.utils import Console
from api.tests.common import make_feature_flag, make_testimonial_auto_share_settings, makeAdmin, makeCommunity, makeTestimonial, makeUser
from database.models import TestimonialSharedCommunity
from database.utils.settings.model_constants.enums import SharingType
from task_queue.nudges.cadmin_testimonial_nudge import get_cadmin_names_and_emails, prepare_testimonials_for_community_admins
from django.utils import timezone

class CadminTestimonialNudgeTestCases(TestCase):
    
    def setUp(self):
        self.c1 = makeCommunity(name="Test Community 1")
        self.c2 = makeCommunity(name="Test Community 2")
        self.c3 = makeCommunity(name="Test Community 3")
        self.c4 = makeCommunity(name="Test Community 4")
        self.c5 = makeCommunity(name="Test Community 5")

        user = makeUser(email="tamUser+23@me.org", full_name="Test Admin")
        user1 = makeUser(email="test+user1@me.com", full_name="Test Admin 1")
        user2 = makeUser(email="test+user2@me.com", full_name="Test Admin 2")
        user3 = makeUser(email="test+user3@me.com", full_name="Test Admin 3")
        user4 = makeUser(email="test+user4@me.com", full_name="Test Admin 4")
        makeAdmin(communities=[self.c1],admin=user)
        makeAdmin(communities=[self.c2],admin=user1)
        makeAdmin(communities=[self.c3],admin=user2)
        makeAdmin(communities=[self.c4],admin=user3)
        makeAdmin(communities=[self.c1],admin=user4)

               
        make_feature_flag(
            key=TESTIMONIAL_AUTO_SHARE_SETTINGS_NUDGE_FEATURE_FLAG_KEY,
            communities=[self.c1, self.c2, self.c3, self.c4, self.c5],
            audience="EVERYONE",
            name="Testimonial Auto Share Settings Nudge"
        )
                
        t1 =makeTestimonial(
            community=self.c2, user=user, title="Testimonial shared to c2 c3, c5",
            sharing_type=SharingType.OPEN_TO.value[0], audience=[self.c2, self.c3, self.c5],
            is_published=True,
            published_at=timezone.now()
        )
        t2 = makeTestimonial(
            community=self.c3, user=user, title="Testimonial shared to none",
            sharing_type=SharingType.OPEN.value[0],
            is_published=True,
            published_at=timezone.now()
        )
        t3 = makeTestimonial(
            community=self.c1, user=user, title="Testimonial shared to none for c1",
            sharing_type=SharingType.OPEN.value[0],
            is_published=True,
            published_at=timezone.now()
        )
        t4 = makeTestimonial(
            community=self.c3, user=user, title="Testimonial shared to none for c3",
            sharing_type=SharingType.OPEN.value[0],
            is_published=True,
            published_at=timezone.now()
        )
        TestimonialSharedCommunity.objects.create(community=self.c2, testimonial=t1)
        TestimonialSharedCommunity.objects.create(community=self.c3, testimonial=t1)
        TestimonialSharedCommunity.objects.create(community=self.c5, testimonial=t1)
        TestimonialSharedCommunity.objects.create(community=self.c1, testimonial=t3)
        TestimonialSharedCommunity.objects.create(community=self.c3, testimonial=t4)
        
    
    def tearDown(self):
        return super().tearDown()
    

    def test_get_cadmin_names_and_emails_success(self):
            
        Console.header("Test get_cadmin_names_and_emails_success for c1")

        data = get_cadmin_names_and_emails(self.c1)
        keys = data.keys()
        self.assertIn('tamUser+23@me.org', keys)
        self.assertIn('test+user4@me.com', keys)
        self.assertIsNotNone(data)



    def test_prepare_testimonials_for_community_admins_success(self):
        Console.header("Test prepare_testimonials_for_community_admins_success")
        task = None
        result = prepare_testimonials_for_community_admins(task)
        self.assertTrue(result)



