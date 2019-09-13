"""
File that contains junk code we don't want to get rid of yet
"""
# def portal_page2(args):
#   """
#   This also retrieves a page by name or id
#   """
#   if "id" in args:
#     return Page.objects.filter(id=args["id"]).first()
#   elif "name" in args:
#     return Page.objects.filter(name=args["name"]).first()
#   return page


# def portal_page3(args):
#   """
#   This also retrieves a page by name or id.

#   Warning.  only use this method if you know the page id or name exists
#   """
#   if "id" in args:
#     try:
#       return Page.objects.get(id=args["id"])
#     except Exception as e:
#       return None
#   elif "name" in args:
#     try:
#       return Page.objects.get(name=args["name"])
#     except Exception as e:
#       return None


# def communities(args):
#   filter_args = {}
#   if "community_id" in args: #shouldnt check id if we want all of the communities
#     filter_args["community"] = args["community_id"]
#   communities =  fetch_from_db(Community, filter_args)
#   return communities


  # I don't think we need a community id for this one, unless event ids are unique in each community but not globally unique
  # if "community_id" in args:
  #   filter_args["community"] = args["community_id"]
  # elif "community_domain" in args:
  #   filter_args["community"] = args["community_domain"]



#   for f in model._meta.get_fields(include_hidden=True):
#     if model in d:
#       d[model][f.name] = type(f)
#     else:
#       d[model] = {f.name: type(f)}

# print(d)
