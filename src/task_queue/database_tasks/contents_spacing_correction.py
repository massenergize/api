from database.models import Action, Event, Testimonial


def correct_spacing_in_actions():
    actions = Action.objects.filter(is_deleted=False)
    for action in actions:
        about = action.about.replace("<p><br></p>", "").replace("<p>.</p>", "").replace("<p>&nbsp;</p>", "")
        deep_dive = action.deep_dive.replace("<p><br></p>", "").replace("<p>.</p>", "").replace("<p>&nbsp;</p>", "")
        action.about = about
        action.deep_dive = deep_dive
        action.save()
    return actions.count()



def correct_spacing_in_events():
    events = Event.objects.filter(is_deleted=False)
    for event in events:
        description = event.description.replace("<p><br></p>", "").replace("<p>.</p>", "").replace("<p>&nbsp;</p>", "")
        event.description = description
        event.save()
    return events.count()


def correct_spacing_in_testimonials():
    testimonials = Testimonial.objects.filter(is_deleted=False)
    for testimonial in testimonials:
        body = testimonial.body.replace("<p><br></p>", "").replace("<p>.</p>", "").replace("<p>&nbsp;</p>", "")
        testimonial.body = body
        testimonial.save()
    return testimonials.count()

def correct_contents_spacing():
    actions = correct_spacing_in_actions()
    print(f"==Corrected {actions} Actions spacing==")
    events = correct_spacing_in_events()
    print(f"==Corrected {events} Actions spacing==")
    testimonials = correct_spacing_in_testimonials()
    print(f"==Corrected {testimonials} Actions spacing==")
    return True
    



