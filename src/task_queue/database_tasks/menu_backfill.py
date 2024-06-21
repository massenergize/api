import logging

from api.utils.api_utils import get_viable_menu_items
from database.models import Community, Menu


def back_fill_menu(communities=None):
    try:
        if not communities:
            communities = Community.objects.filter(is_deleted=False)
        for community in communities:
            
            menu = Menu.objects.filter(community=community, is_custom=False).first()
            if menu:
                logging.warning(f"=== Back filling menu for {community.name}: Menu already exists ")
                continue
                
            prepared_menu = get_viable_menu_items(community)
            
            menu = Menu(
                name = f"{community.subdomain} Main Menu",
                community=community,
                content=prepared_menu["PortalMainNavLinks"],
                is_custom=False,
                footer_content=prepared_menu["PortalFooterQuickLinks"],
                contact_info=prepared_menu["PortalFooterContactInfo"],
                is_published=True
            )
            menu.save()
            logging.info(f"=== Back filling menu for {community.name}: Done ")
            
        logging.info("=== Back filling menu: Done")
        to_return = {"success": True, "error": None}
        return to_return
    except Exception as e:
        logging.error(f"=== Back filling menu: Exception: {str(e)} ")
        return {"success": False, "error": str(e)}
        
        
    
