"""
This is the test file for feature flags
"""
from datetime import datetime, timedelta
import time
from django.test import TestCase, Client
from django.utils import timezone

from _main_.utils.common import serialize
from _main_.utils.feature_flags.FeatureFlagConstants import FeatureFlagConstants
from _main_.utils.utils import Console
from database.models import FeatureFlag, Community, CommunityAdminGroup
from urllib.parse import urlencode
from api.tests.common import (
    makeAdminGroup,
    makeCommunity,
    makeFlag,
    makeUser,
    signinAs,
    createUsers,
)

ROUTES = {
    "add": "/api/featureFlags.add",
    "delete": "/api/featureFlag.delete",
    "update": "/api/featureFlag.update",
    "list": "/api/featureFlags.list_for_super_admins",
    "get": "/api/featureFlags.list",
    "info": "/api/featureFlags.info"
}


class FeatureFlagHandlerTest(TestCase):
    @classmethod
    def tearDownClass(self):
      pass

    def setUp(self):
      pass

    @classmethod
    def setUpClass(self):
        Console.header("TESTING FEATURE FLAGS")
        self.client = Client()
        self.USER, self.CADMIN, self.SADMIN = createUsers()

    def test_info(self):
        signinAs(self.client, None)
        Console.header("Fetching Flag Information")
        flags = [ makeFlag(name ="Flag Number - "+ str(i)) for i in range(4)]
        for ff in flags:
            response = self.client.post(
                ROUTES["info"],
                urlencode({"id": ff.id}),
                content_type="application/x-www-form-urlencoded",
            ).toDict()
            self.assertTrue(response.get("success"))
            data = response.get("data", {})
            expected = serialize(ff, True)
            self.assertEqual(expected.get("id"), data.get("id"))
            self.assertEqual(expected.get("name"), data.get("name"))
        Console.underline("Feature Flag Info Route Works Well")



    def test_only_sadmins_can_create_flags(self):
        """
        Sign in as Normal user
        Sign in as community admin
        Run requests to add a new feature flag, and expect persmission_denied error
        """
        signinAs(self.client, self.USER)
        Console.header("Test That Only SADMINS Can Create Flags")
        userRequestResponse = self.client.post(ROUTES["add"], {}).toDict()
        normalAdminRequestResponse = self.client.post(ROUTES["add"], {}).toDict()

        self.assertEquals(userRequestResponse.get("error"), "permission_denied")
        self.assertEquals(normalAdminRequestResponse.get("error"), "permission_denied")

    def test_delete_feature_flag(self):
        """
        Create a new flag,
        With the known id of the just-created flag,
        run a request to the delete route
        Successful request should return the id of the just-deleted
        item
        """
        signinAs(self.client, self.SADMIN)
        Console.header("Deleting Feature Flag")
        flag = makeFlag(name = "Flag that is going to be deleted soon")
        response = self.client.post(ROUTES["delete"],{"id":str(flag.id)}).toDict()

        self.assertEquals(flag.id, response.get("data"))
        Console.underline("Deleted flag successfuly, deleting works!")

    def test_updating_feature_flag(self):
        """
        Expectation: All of the feature flag fields can can be updated through
        the update route
        """
        signinAs(self.client, self.SADMIN)
        Console.header("Updating Feature Flag")
        coms = []
        users = []

        # Create 3 communities & 3 Users
        for i in range(3):
            coms.append(makeCommunity(name="Community - " + str(i)))
            users.append(makeUser(name="User - " + str(i)))

        # Create a flag and link 2 of the communities & users to it
        flag = makeFlag(communities=coms[:2], users=users[:2])

        me_coms = [str(c.id) for c in flag.communities.all()]
        me_users = [str(u.id) for u in flag.users.all()]
        print("Created Feature Flag with communities & Users")

        data = {
            "id": str(flag.id),
            "name": "Flag updated - edited",
            "notes": "This is a description I am passing as an update",
            "audience": FeatureFlagConstants.for_specific_audience(),
            "scope": FeatureFlagConstants.for_admin_frontend(),
            "community_ids": [str(coms[2].id)],
            "user_ids": [str(users[2].id)],
        }
        print("Sending request to update flag with new content...")

        # Send a request to update the fields, this time with only 1 diff community, & 1 diff user
        response = self.client.post(
            ROUTES["update"],
            data
        ).toDict()
        content = response.get("data")

        self.assertEquals(data.get("name"), content.get("name"))
        self.assertEquals(data.get("notes"), content.get("notes"))
        self.assertEquals(data.get("scope"), content.get("scope"))

        coms_after = [str(com.get("id")) for com in content.get("communities")]
        users_after = [str(user.get("id")) for user in content.get("users")]

        self.assertListEqual(data.get("community_ids"), coms_after)
        self.assertListEqual(data.get("user_ids"), users_after)

        Console.underline("Feature flag updated was successful!")

    def test_use_feature_flags_backend(self):
        """
        Test backend feature flag like used in nudges,
        Expectations:  can be enabled for specific users or communities, and can 
        """
        Console.header("Fetching User Features on User Portal (NOT - Authenticated)")

        print(
            "Created flag with (specific flag, non related flag, universal flag..."
        )

        my_community = makeCommunity(subdomain="my_community")
        another_community = makeCommunity(subdomain="another_community")
        my_community_nudge_flag = makeFlag(
            name="single-community-nudge",
            communities=[my_community],
            audience=FeatureFlagConstants.for_specific_audience(),
        )
        all_community_nudge_flag = makeFlag(name="all-community-nudge")
        today = timezone.now()
        last_week = today - timedelta(days=7)

        expired_flag = makeFlag(name="expired-flag",expires_on=last_week)
                                
        key = 'single-community-nudge-feature'
        flag1 = FeatureFlag.objects.get(key=key)

        allCommunities = Community.objects.all()
        self.assertTrue(flag1.enabled())

        flagCommunities = flag1.enabled_communities(allCommunities)
        self.assertEqual(flagCommunities.count(),1)

        key2 = "all-community-nudge-feature"
        flag2 = FeatureFlag.objects.get(key=key2)
        flag2Communities = flag2.enabled_communities(allCommunities)
        self.assertEqual(flag2Communities.count(),allCommunities.count())

        key3 = 'expired-flag-feature'
        flag3 = FeatureFlag.objects.get(key=key3)
        self.assertFalse(flag3.enabled())

    def test_get_feature_flags_on_portal(self):
        """
        No signed in user will be available here,
        Expectations:  Loading feature flags that are only for frontend portal, and the community with the current subdomain
        """
        Console.header("Fetching User Features on User Portal (NOT - Authenticated)")

        print(
            "Created flag with (specific flag, non related flag, universal flag..."
        )

        some_other_flag = makeFlag(
            audience=FeatureFlagConstants.for_specific_audience(),
            user_audience=FeatureFlagConstants.for_specific_audience(),
        )
        community = makeCommunity(subdomain="ablekuma")
        ablekuma_flag = makeFlag(
            name="Speficific Ablekuma Feature",
            communities=[community],
            audience=FeatureFlagConstants.for_specific_audience(),
        )
        flag_for_everyone = makeFlag(name="Flag For Everyone")

        print("Sending request to retrieve flags specific to subdomain...")

        response = self.client.post(ROUTES["get"], {"subdomain": "ablekuma"}).toDict()
        content = response.get("data")
        features = content.get("features")

        self.assertTrue(content.get("count") == 2)
        self.assertTrue(
            features.get(ablekuma_flag.key) and features.get(flag_for_everyone.key)
        )
        self.assertEquals(features.get(some_other_flag.key), None)

        Console.underline("Response list contains all the right features!")

    def test_get_feature_flags_for_user_on_portal(self):
        """
        Expectations:
        1. Flags specific to the signed in user on portal
        2. Flags specific to the community the user is visiting from, on the portal
        3. Flags for everyone
        """
        signinAs(self.client, self.USER)
        Console.header("Fetching User Features on User Portal (Authenticated)")
        
        user_specific_flag = makeFlag(
            name="User Specific Flag",
            user_audience=FeatureFlagConstants.for_specific_audience(),
            users=[self.USER],
        )
        community = makeCommunity(subdomain="ablekuma")
        community_specific = makeFlag(
            name="Community Specific", communities=[community]
        )
        general_flag = makeFlag(
            name="Flag for everyone", scope=FeatureFlagConstants.for_admin_frontend()
        )
        some_other_flag = makeFlag(
            audience=FeatureFlagConstants.for_specific_audience(),
            user_audience=FeatureFlagConstants.for_specific_audience(),
        )

        print(
            "Sending request to retrieve flags specific to user and subdomain on portal..."
        )

        response = self.client.post(
            ROUTES["get"], {"subdomain": community.subdomain}
        ).toDict()
        content = response.get("data")
        features = content.get("features")

        self.assertTrue(content.get("count") == 2)
        self.assertTrue(
            features.get(user_specific_flag.key)
            and features.get(community_specific.key)
        )
        self.assertEquals(features.get(some_other_flag.key), None)
        self.assertEquals(features.get(general_flag.key), None)

        Console.underline("Response list contains all the right features!")

    def test_get_feature_flags_for_community_admin(self):
        """
        1. Flags specific to the signed in admin and on the admin portal
        2. Flags specific to all the communities that an admin is in charge of on the admin portal
        3. Flags available to everyone
        """

        signinAs(self.client, self.CADMIN)
        Console.header("Fetching CADMIN Features on Admin Portal")
        com1 = makeCommunity(name="Admin Community 1")
        group1 = makeAdminGroup(community=com1, members=[self.CADMIN])
        com1.communityadmingroup_set.add(group1)
        com2 = makeCommunity(name="Admin Community 2 ")
        group2 = makeAdminGroup(community=com2, members=[self.CADMIN])
        com2.communityadmingroup_set.add(group2)

        user_specific_flag = makeFlag(
            name="User Specific Flag - Admin Frontend",
            user_audience=FeatureFlagConstants.for_specific_audience(),
            scope=FeatureFlagConstants.for_admin_frontend(),
            users=[self.CADMIN],
        )
        user_specific_flag_portal = makeFlag(
            name="User Specific Flag - Frontend",
            user_audience=FeatureFlagConstants.for_specific_audience(),
            scope=FeatureFlagConstants.for_user_frontend(),
            users=[self.CADMIN],
        )
        community1_specific = makeFlag(
            name="Community1 Specific",
            communities=[com1],
            audience=FeatureFlagConstants.for_specific_audience(),
            scope=FeatureFlagConstants.for_admin_frontend(),
        )
        community2_specific = makeFlag(
            name="Community2 Specific",
            communities=[com2],
            audience=FeatureFlagConstants.for_specific_audience(),
            scope=FeatureFlagConstants.for_admin_frontend(),
        )
        general_flag = makeFlag(
            name="Flag for everyone", scope=FeatureFlagConstants.for_admin_frontend()
        )
        some_other_flag = makeFlag(
            audience=FeatureFlagConstants.for_specific_audience(),
            user_audience=FeatureFlagConstants.for_specific_audience(),
        )

        print(
            "Sending request to retrieve flags specific to user and subdomain on portal..."
        )

        response = self.client.post(ROUTES["get"], {"is_admin": True}).toDict()
        content = response.get("data")
        features = content.get("features")

        self.assertTrue(content.get("count") == 4)
        self.assertTrue(
            features.get(user_specific_flag.key)
            and features.get(community1_specific.key)
            and features.get(community2_specific.key)
            and features.get(general_flag.key)
        )
        self.assertEquals(features.get(user_specific_flag_portal.key), None)
        self.assertEquals(features.get(some_other_flag.key), None)

        Console.underline("Response list contains all the right features!")
