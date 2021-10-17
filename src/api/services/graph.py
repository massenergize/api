from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.graph import GraphStore
from _main_.utils.context import Context
from typing import Tuple

class GraphService:
  """
  Service Layer for all the graphs
  """

  def __init__(self):
    self.store =  GraphStore()

  def get_graph_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    graph, err = self.store.get_graph_info(context, args)
    if err:
      return None, err
    return serialize(graph, full=True), None

  def list_graphs(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    graphs, err = self.store.list_graphs(context, args)
    if err:
      return None, err
    return graphs, None

  def graph_actions_completed(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    graph, err = self.store.graph_actions_completed(context, args)
    if err:
      return None, err
    return graph, None

  def graph_actions_completed_by_team(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    graph, err = self.store.graph_actions_completed_by_team(context, args)
    if err:
      return None, err
    return graph, None

  def graph_community_impact(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    graph, err = self.store.graph_communities_impact(context, args)
    if err:
      return None, err
    return graph, None


  def create_graph(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    graph, err = self.store.create_graph(context, args)
    if err:
      return None, err
    return serialize(graph), None


  def update_graph(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    graph, err = self.store.update_graph(context, args)
    if err:
      return None, err
    return serialize(graph), None

  def delete_graph(self, context, graph_id) -> Tuple[dict, MassEnergizeAPIError]:
    graph, err = self.store.delete_graph(context, graph_id)
    if err:
      return None, err
    return serialize(graph), None


  def list_graphs_for_community_admin(self, context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    graphs, err = self.store.list_graphs_for_community_admin(context, community_id)
    if err:
      return None, err
    return graphs, None


  def list_graphs_for_super_admin(self, context) -> Tuple[list, MassEnergizeAPIError]:
    graphs, err = self.store.list_graphs_for_super_admin(context)
    if err:
      return None, err
    return graphs, None

  def update_data(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    data, err = self.store.update_data(context, args)
    if err:
      return None, err
    return serialize(data), None

  def delete_data(self, context, data_id) -> Tuple[dict, MassEnergizeAPIError]:
    result, err = self.store.delete_data(context, data_id)
    if err:
      return None, err
    return result, None