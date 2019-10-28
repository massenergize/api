from database.models import Community, UserProfile, Media, AboutUsPageSettings, ActionsPageSettings, ContactUsPageSettings, DonatePageSettings, HomePageSettings, ImpactPageSettings, Goal
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse

class CommunityStore:
  def __init__(self):
    self.name = "Community Store/DB"

  def get_community_info(self, args) -> (dict, MassEnergizeAPIError):
    try:
      community = Community.objects.filter(**args).first()
      if not community:
        return None, InvalidResourceError()
      return community, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_communities(self) -> (list, MassEnergizeAPIError):
    try:
      communities = Community.objects.filter(is_deleted=False, is_approved=True)
      if not communities:
        return [], None
      return communities, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def create_community(self, args) -> (dict, MassEnergizeAPIError):
    try:
      logo = args.pop('logo', None)
      new_community = Community.objects.create(**args)

      if logo:
        cLogo = Media(file=logo, name=f"{args.get('name', '')} CommunityLogo")
        cLogo.save()
        new_community.logo = cLogo
      

      #create a goal for this community
      community_goal = Goal.objects.create(name=f"{new_community.name}-Goal")
      new_community.goal = community_goal
      new_community.save()


      #now create all the pages
      aboutUsPage = AboutUsPageSettings.objects.filter(is_template=True).first()
      if aboutUsPage:
        aboutUsPage.pk = None
        aboutUsPage.title = f"About {new_community.name}"
        aboutUsPage.community = new_community
        aboutUsPage.is_template = False
        aboutUsPage.save()

      actionsPage = ActionsPageSettings.objects.filter(is_template=True).first()
      if actionsPage:
        actionsPage.pk = None
        actionsPage.title = f"Actions for {new_community.name}"
        actionsPage.community = new_community
        actionsPage.is_template = False
        actionsPage.save()

      contactUsPage = ContactUsPageSettings.objects.filter(is_template=True).first()
      if contactUsPage:
        contactUsPage.pk = None 
        contactUsPage.title = f"Contact Us - {new_community.name}"
        contactUsPage.community = new_community
        contactUsPage.is_template = False
        contactUsPage.save()
      
      donatePage = DonatePageSettings.objects.filter(is_template=True).first()
      if donatePage:
        donatePage.pk = None 
        donatePage.title = f"Take Actions - {new_community.name}"
        donatePage.community = new_community
        donatePage.is_template = False
        donatePage.save()
      
      homePage = HomePageSettings.objects.filter(is_template=True).first()
      images = homePage.images.all()
      #TODO: make a copy of the images instead, then in the home page, you wont have to create new files everytime
      if homePage:
        homePage.pk = None 
        homePage.title = f"Welcome to Massenergize, {new_community.name}!"
        homePage.community = new_community
        homePage.is_template = False
        homePage.save()
        homePage.images.set(images)
      
      impactPage = ImpactPageSettings.objects.filter(is_template=True).first()
      if impactPage:
        impactPage.pk = None 
        impactPage.title = f"See our Impact - {new_community.name}"
        impactPage.community = new_community
        impactPage.is_template = False
        impactPage.save()

      return new_community, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def update_community(self, community_id, args) -> (dict, MassEnergizeAPIError):
    try:
      logo = args.pop('logo', None)
      community = Community.objects.filter(id=community_id)
      if not community:
        return None, InvalidResourceError()
      
      community.update(**args)

      new_community = community.first()
      if logo and new_community.logo:
        # new_community.logo.file = logo
        # new_community.logo.save()
        cLogo = Media(file=logo, name=f"{args.get('name', '')} CommunityLogo")
        cLogo.save()
        new_community.logo = cLogo
        new_community.save()

      return new_community, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def delete_community(self, args) -> (dict, MassEnergizeAPIError):
    try:
      communities = Community.objects.filter(**args)
      communities.delete()
      return communities, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_communities_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    communities = Community.objects.filter(community__id = community_id)
    return communities, None


  def list_communities_for_super_admin(self):
    try:
      communities = Community.objects.filter(is_deleted=False)
      return communities, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))