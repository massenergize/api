from unittest import TestCase
from django.test import Client
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.utils import Console
from api.tests.common import (
    createUsers,
    makeAction,
    makeAdmin,
    makeCommunity,
    makeFootage,
    makeMembership,
    makeMessage,
    makeTeam,
    makeTestimonial,
    makeUser,
    makeUserActionRel,
    signinAs,
)


class TestUserEngagements(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Console.header("Testing Admin User Engagement & What  to Do Next")


    def test_user_engagement_summary(self):
        """
            The idea, is to 
            1. Create a few communities 
            2. Create users(normal)  
            3. Make one user an admin of a few of the communities
            4. Then make some actions that belong to the cadmin's communities 
            5. After, the remaining normal users should sign in to some communities 
            6. Complete actions, 
            7. And add some actions as to do. 
            Criteria for success 
            If the engagement route works as it should, it will only retrieve the sign in footages, 
            actions that have been completed, and ones that have been added todo for only the communiities 
            that the current admin manages
        """
        client = Client()
        Console.header("Testing Admin User Engagements")
        users = []
        communities = []

        for i in range(3):
            user = makeUser(name=f"User Number - {i+1}")
            users.append(user)
        for i in range(3):
            com = makeCommunity()
            communities.append(com)

        a1 = makeAction(community=communities[0])
        a2 = makeAction(community=communities[0])
        a3 = makeAction(community=communities[1])
        a4 = makeAction(community=communities[1])
        a5 = makeAction(community=communities[2])
        
        # 3 different users mark an action as todo, but only 2 actions are involved (so only 2 communities will be involved)
        # Which should be the 2 community that the current signed in admin will be in charge of
        d1 = makeUserActionRel(action=a1, user=users[0], status="DONE")
        d2 = makeUserActionRel(action=a2, user=users[1], status="DONE")
        d3 = makeUserActionRel(action=a1, user=users[2], status="DONE")

        # 2 users mark actions as todo. 4 actions involved, But only 3 of the actions are created in the communities 
        # that the currently signed in admin manages
        td1 = makeUserActionRel(action=a1, user=users[0], status="TODO")
        td2 = makeUserActionRel(action=a2, user=users[0], status="TODO")
        td3 = makeUserActionRel(action=a4, user=users[1], status="TODO")
        td4 = makeUserActionRel(action=a5, user=users[1], status="TODO")

        # 4 sign in footages. Only 3 of them are stationed in the admin's communities
        f1 = makeFootage(
            actor=users[0],
            communities=communities[1:2], 
            activity_type=FootageConstants.sign_in(),
            portal=FootageConstants.on_user_portal(),
        )
        f2 = makeFootage(
            actor=users[1],
            communities=communities[:1],
            activity_type=FootageConstants.sign_in(),
            portal=FootageConstants.on_user_portal(),
        )
        f3 = makeFootage(
            actor=users[0],
            communities=communities[1:],
            activity_type=FootageConstants.sign_in(),
            portal=FootageConstants.on_user_portal(),
        )
        f4 = makeFootage(
            actor=users[2],
            communities=communities[2:],
            activity_type=FootageConstants.sign_in(),
            portal=FootageConstants.on_user_portal(),
        )


        cadmin = makeAdmin(communities=communities[:2])
        signinAs(client, cadmin)

        response = client.post(
            "/api/summary.get.engagements", {"time_range": "last-month"}
        ).json().get("data",{})
        
        done = response.get("done_interactions",{}).get('data',[])
        done_count = response.get("done_interactions",{}).get("count",0)
        todos = response.get("todo_interactions",{}).get('data',[])
        todo_count = response.get("todo_interactions",{}).get("count",0)
        sign_ins = response.get("sign_ins",{}).get('data',[])
        sign_in_count = response.get("sign_ins",{}).get("count",0)

        self.assertEquals(done_count,3)
        self.assertEquals(todo_count,3)
        self.assertEquals(sign_in_count,3)
       
        self.assertTrue(a5.id not in todos)
        self.assertTrue(a1.id  in done)
        self.assertTrue(a2.id  in done)
        print("Todo, Done, and Sign in engagements retrieved!")

        self.assertTrue(users[0].email  in sign_ins)
        self.assertTrue(users[1].email  in sign_ins)
        self.assertTrue(users[2].email  not in sign_ins)
        print("The right values were retrieved!")
        

    def test_admin_next_steps(self):
        """
            Idea 
            1. Again, create a few users 
            2. Create a few communities 
            3. Make one of the users an admin of a few of the communities 
            4. Create testimonials for various communities 
            5. Create actions for various communities 
            6. Create messages (that look they were sent by users)
            Criteria for success 
            if the route works as it should, it will retrieve all unanswered actions, tesitmonials, 
            messages that are related to any of the communities that the cadmin manages

        """
        client = Client()
        Console.header("Admin Next Steps")
        users = []
        communities = []
        for i in range(3):
            user = makeUser(name=f"User Number - {i+1}")
            users.append(user)
        for i in range(3):
            com = makeCommunity()
            communities.append(com)

        cadmin = makeAdmin(communities = communities[:2])
       
        makeMembership(user = users[0], community = communities[0])
        makeMembership(user = users[1], community = communities[1])

        testimonial = makeTestimonial(user = users[0], community=communities[0])
        testimonial2 = makeTestimonial(user = users[0], community=communities[0])
        testimonial3 = makeTestimonial(user = users[1], community=communities[1])

        m1 = makeMessage(user=users[0], community = communities[0])
        m2 = makeMessage(user=users[1], community = communities[1])
        m3 = makeMessage(user=users[1], community = communities[2])

        t1 = makeTeam(community = communities[0])
        t2 = makeTeam(community = communities[0])
        t3 = makeTeam(community = communities[1])
        t4 = makeTeam(community = communities[1], is_published=True)
        t3 = makeTeam(community = communities[2])
        signinAs(client, cadmin)

        response = client.post(
            "/api/summary.next.steps.forAdmins"
        ).json().get("data",{})
        testimonials = response.get("testimonials",{}).get("data",[])
        teams = response.get('teams',{}).get("data",[])
        messages = response.get('messages').get("data",[])
        
        self.assertEquals(len(testimonials),3)
        self.assertEquals(len(teams),3)
        self.assertEquals(len(messages),2)

        print("Items for admins to attend to checkout!")
