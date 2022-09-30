from django.shortcuts import render
import re

# Create your views here.

#class UserAvatarUpload(APIView):
#    permission_classes = [permissions.IsAuthenticated]
#    parser_classes - [MultiPartParser, FormParser]
def clean_all_selected_subdomains(self, request, qs):
    for s in qs:
        new_name = s.name.strip()
        
        # replaces spaces with underscores
        new_name = re.sub(' ', '_', s.name)

        # filters out non-alphanumeric characters (excluding underscores)
        new_name = re.sub(r"[^A-Za-z0-9_]", "", new_name)

        # accounts for leading underscores
        new_name = re.sub(r"^[_]+", "", new_name)
        
        # accounts for trailing underscores
        new_name = re.sub(r"[_]+$", "", new_name)
        
        # if new_name == s.name:
        #     print("Not changing '{}'\n".format(s.name))
        # else:
        #     print("Changing '{}' to '{}'\n".format(s.name, new_name))
        
        s.name = new_name
        s.save()
