from django.shortcuts import render
from database.models import UserProfile
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments

# Create your views here.

#class UserAvatarUpload(APIView):
#    permission_classes = [permissions.IsAuthenticated]
#    parser_classes - [MultiPartParser, FormParser]
def make_usernames_not_unique(self, request, qs):
    for user in qs:
        user.preferred_name = "md"
        user.save()

def make_selected_usernames_unique(self, request, qs):
    # key is username, value is list of UserProfile objects with that username
    usernames = {}
    
    # stores the usernames that belong to more than one user 
    non_unique_usernames = set()

    # users = UserProfile.objects.all()
    # if 'qs' is used instead of 'users', superadmin MUST select al users in admin page

    for user in qs:
        name = user.preferred_name

        if name in usernames:
            usernames[name].append(user)
            non_unique_usernames.add(name)
        else:
            usernames[name] = [user]
    
    # printing out non-unqiue usernames
    for name in non_unique_usernames:
        print("Username '{}' is held by:".format(name))
        
        names = usernames[name]
        for n in names:
            print("\t{} - {}".format(n.full_name, n.email))

    # updating non-unique usernames
    for name in non_unique_usernames:
        names = usernames[name][1:] # the first UserProfile can keep their original username
        num = 1 # start at 1 or 0?

        for n in names:
            # generating new username
            new_username = n.preferred_name + "-" + str(num)
            while new_username in usernames.keys():
                num += 1
                new_username = n.preferred_name + "-" + str(num)

            # updating 'usernames' to have the newly created ones
            usernames[new_username] = n
            
            print("Changing username of {} from {} to {}".format(n.email, n.preferred_name, new_username))
            n.preferred_name = new_username
            n.save()

            # sending email to user informing of change
            template_model = {
                'name'         : n.full_name.split(" ")[0], # just gets first name, is full name better?
                'new_username' : new_username,
                'old_username' : name
            }
            to = "mattia.danese@massenergize.org" # n.email
            template_id = 28696806
            
            send_massenergize_email_with_attachments(template_id, template_model, to, None, None)