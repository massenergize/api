from django.test import TestCase
from api.store.testimonial import get_auto_shared_with_list
from api.tests.common import make_tag, makeCommunity, makeLocation, makeTestimonial
from database.models import TestimonialAutoShareSettings, LocationType

class TestGetAutoSharedWithList(TestCase):

    def setUp(self):
        loc1 = makeLocation(state="MA", zipcode="02112", city="Boston")
        loc4 = makeLocation(state="NY", zipcode="02115", city="City")
        
        self.c1 = makeCommunity(name="Community - test 1", locations=[loc1.id] )
        self.c2 = makeCommunity(name="Community - test 2",locations=[loc4.id])
        self.c3 = makeCommunity(name="Community - test 3",)
        self.c4 = makeCommunity(name="Community - test 4", )

        self.testimonial = makeTestimonial(title="SHareable Testimonial")


        self.tag1 = make_tag(name="Solar")
        self.tag2 = make_tag(name="Waste")
        
    def test_get_auto_shared_with_list_no_testimonial(self):
        result = get_auto_shared_with_list(None)
        self.assertEqual(result, [])


    def test_get_auto_shared_with_list_no_community(self):
        testimonial = makeTestimonial(title="SHareable Testimonial 2223")
        result = get_auto_shared_with_list(testimonial)
        self.assertEqual(result, [])

    def test_get_auto_shared_with_list_no_auto_share_settings(self):
        self.testimonial.community = makeCommunity(name="Community - test Within")
        result = get_auto_shared_with_list(self.testimonial)
        self.assertEqual(result.first(), None)

    def test_get_auto_shared_with_list_geographical_range(self):
        self.testimonial.community = self.c1
        self.testimonial.save()
        TestimonialAutoShareSettings.objects.create(
            community=self.c3,
            share_from_location_type=LocationType.STATE.value[0],
            share_from_location_value='MA'
        )
        result = get_auto_shared_with_list(self.testimonial)
        self.assertIn(self.c3, list(result))

    def test_get_auto_shared_with_list_tags(self):
        self.testimonial.community = self.c1
        self.testimonial.tags.add(self.tag1)
        self.testimonial.save()
        auto_share_settings = TestimonialAutoShareSettings.objects.create(
            community=self.c4,
        )
        # auto_share_settings.excluded_tags.add(self.tag1)
        auto_share_settings.share_from_communities.set([self.c1])
        result = get_auto_shared_with_list(self.testimonial)
        self.assertIn(self.c4, list(result))

    def test_get_auto_shared_with_list_communities(self):
        self.testimonial.community = self.c1
        self.testimonial.save()
        auto_share_settings = TestimonialAutoShareSettings.objects.create(
            community=self.c2,
        )
        auto_share_settings.share_from_communities.set([self.c1])
        result = get_auto_shared_with_list(self.testimonial)
        self.assertIn(self.c2, list(result))
