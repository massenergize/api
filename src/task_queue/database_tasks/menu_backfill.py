from api.utils.api_utils import get_viable_menu_items
from database.models import Community, Menu


def backfill_menu():
	try:
		communities = Community.objects.filter(is_deleted=False)
		for community in communities:
			
			menu = Menu.objects.filter(community=community, is_custom=False).first()
			if menu:
				print("=== Backfilling menu for community: Menu already exists ", community.name)
				continue
				
			prepared_menu = get_viable_menu_items(community)
			
			menu = Menu(
				name = f"{community.name} Main Menu",
				community=community,
				content=prepared_menu["PortalMainNavLinks"],
				is_custom=False,
				footer_content=prepared_menu["PortalFooterQuickLinks"],
				contact_info=prepared_menu["PortalFooterContactInfo"],
				is_published=True
			)
			menu.save()
			print("=== Backfilling menu for community: Done ", community.name)
				
		print("=== Backfilling menu: Done")
	except Exception as e:
		print("=== Backfilling menu: Error ", e)
		return None, e
			
			
	
