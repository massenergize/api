from database.models import *

class BloatDB:
    def __init__(self):
        pass

    def bloat_now(self):
        self.bloat_testimonials()
        self.bloat_actions()

    def bloat_actions(self):
        com = Community.objects.filter(name__icontains="Wayland").first()
        for x in range(1000):
            action = Action()
            action.title = f"Bloated Actions {x+1}0{x}"
            action.is_published = True
            action.community = com
            action.is_approved = True
            action.save()
            print(f"Bloated Actions 0{x}")


    def bloat_testimonials(self):
        com = Community.objects.filter(name__icontains="Wayland").first()
        action = Action.objects.filter(title__icontains="Bloated Actions").first()
        user = UserProfile.objects.get(email="abdullai.tahiru@gmail.com")
        for x in range(1000):
            testimonial = Testimonial()
            testimonial.title = f"Bloated Testimonial {x+1}0{x}"
            testimonial.community = com
            testimonial.is_published=True
            testimonial.is_approved = True
            testimonial.action = action
            testimonial.user = user
            testimonial.save()
            print(f"Bloated Testimonial 0{x}")
