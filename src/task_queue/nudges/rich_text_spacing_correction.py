from database.models import Action, Event, Testimonial

# criteria_list = ["<p><br></p>", "<p>.</p>", "<p>&nbsp;</p>"]


def correct_spacing_in_actions():
    actions = Action.objects.filter(is_deleted=False)
    print(f"== Correcting spacing in {actions.count()}actions ==")
    for action in actions:
        about = action.about.replace("<p><br></p>", "").replace("<p>.</p>", "").replace("<p>&nbsp;</p>", "")
        deep_dive = action.deep_dive.replace("<p><br></p>", "").replace("<p>.</p>", "").replace("<p>&nbsp;</p>", "")
        action.about = about
        action.deep_dive = deep_dive
        action.save()
    print("== Done Correcting spacing in actions ==")



def correct_spacing_in_events():
    events = Event.objects.filter(is_deleted=False)
    print(f"== Correcting spacing in {events.count()}events ==")
    for event in events:
        description = event.description.replace("<p><br></p>", "").replace("<p>.</p>", "").replace("<p>&nbsp;</p>", "")
        event.description = description
        event.save()
    print("== Done Correcting spacing in events==")


def correct_spacing_in_testimonials():
    testimonials = Testimonial.objects.filter(is_deleted=False)
    print(f"== Correcting spacing in {testimonials.count()}testimonials ==")
    for testimonial in testimonials:
        body = testimonial.body.replace("<p><br></p>", "").replace("<p>.</p>", "").replace("<p>&nbsp;</p>", "")
        testimonial.body = body
        testimonial.save()
    print("== Done Correcting spacing in testimonials ==")

def correct_contents_spacing():
    correct_spacing_in_actions()
    correct_spacing_in_events()
    correct_spacing_in_testimonials()