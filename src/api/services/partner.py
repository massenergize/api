

from _main_.utils.common import serialize, serialize_all
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from typing import Tuple
from api.store.partner import PartnerStore



class PartnerService:
    """
    Service Layer for all the partners
    """

    def __init__(self):
        self.store =  PartnerStore()

    def get_partner_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.get_partner_info(context, args)
        if err:
             return None, err
        return serialize(res, full=True), None
    

    def list_partners(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.list_partners(context, args)
        if err:
            return None, err
        return serialize_all(res, full=True), None
    

    def create_partner(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.create_partner(context, args)
        if err:
            return None, err
        
        return serialize(res, full=True), None
    

    def update_partner(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.update_partner(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None
    

    def delete_partner(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        partner, err = self.store.delete_partner(context, args)
        if err:
            return None, err
        return serialize(partner), None
    

    def list_partners_for_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.list_partners_for_admin(context, args)
        if err:
            return None, err
        return serialize_all(res, full=True), None