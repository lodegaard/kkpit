import copy
import datetime
from collections import OrderedDict

from .actionfetcher import ActionFetcher

class ProgressChartProcessor:
    fmt = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, client):
        ''''''
        self.client = client
        self.fetcher = ActionFetcher(client)

    def _process(self, data):
        actions = data["actions"]
        lists = data["lists"]

        output_data = {}
        prev_date = None
        for action in sorted(actions, key=lambda action: datetime.datetime.strptime(action["date"], self.fmt)):
            action_date = datetime.datetime.strptime(action["date"], self.fmt)
            action_rounded_date = datetime.datetime(action_date.year, action_date.month, action_date.day, action_date.hour-(action_date.hour%4))
            
            if not action_rounded_date in output_data.keys():
                # Add the date
                if prev_date is None:
                    output_data[action_rounded_date] = {}
                    for list_ in lists:
                        # Add all the lists that could have elements on this date
                        # If this is the first action for this data, no lists have any cards yet
                        output_data[action_rounded_date][list_.name] = set()
                elif prev_date is not None and action_rounded_date not in output_data.keys():
                    # If there are no changes the number of cards in a list is the same as before
                    output_data[action_rounded_date] = copy.deepcopy(output_data[prev_date])
                    
            
            # Keep track of the previous inserted date
            prev_date = action_rounded_date

            matching_list = None
            if action["type"] == 'updateCard':
                if 'listBefore' in action["data"].keys() and 'listAfter' in action["data"].keys():
                    matching_list = action["data"]["listAfter"]["name"]
                    prev_list = action["data"]["listBefore"]["name"]

                    if action["data"]["card"]["id"] in output_data[action_rounded_date][prev_list]:
                        #print('{}: {} => -- {}'.format(action_rounded_date, prev_list, action["data"]["card"]["name"]))
                        output_data[action_rounded_date][prev_list].remove(action["data"]["card"]["id"])

                elif 'closed' in action["data"]["card"].keys():
                    if 'closed' in action["data"]["old"].keys() and not action["data"]["old"]["closed"]:
                        prev_list = action["data"]["list"]["name"]
                        output_data[action_rounded_date][prev_list].remove(action["data"]["card"]["id"])

                elif 'listAfter' in action["data"].keys():
                    print('Update card with undefined after')
                elif 'listBefore' in action["data"].keys():
                    print('Update card with undefined before')

            elif action["type"] == 'createCard' and 'name' in action["data"]["list"]:
                matching_list = action["data"]["list"]["name"]

            elif action["type"] == 'convertToCardFromCheckItem' and 'name' in action["data"]["list"]:
                matching_list = action["data"]["list"]["name"]

            elif action["type"] == 'moveCardToBoard' and 'name' in action["data"]["list"]:
                matching_list = action["data"]["list"]["name"]

            elif action["type"] == 'moveCardFromBoard' and 'name' in action["data"]["list"]:
                prev_list = action["data"]["list"]["name"] 
                if action["data"]["card"]["id"] in output_data[action_rounded_date][prev_list]:
                    #print('{}: {} => -- {}'.format(action_rounded_date, prev_list, action["data"]["card"]["name"]))
                    output_data[action_rounded_date][prev_list].remove(action["data"]["card"]["id"])

            elif action["type"] == 'updateList':
                if 'old' in action["data"].keys() and 'name' in action["data"]["old"]:
                    if action["data"]["old"]["name"] == 'Done':
                        #print('{}: Clearing done list after archiving'.format(action_rounded_date))
                        output_data[action_rounded_date]['Done'].clear()
            #else:
                #print('{}: Card is probably deleted -- {}'.format(action_rounded_date, action))

            if matching_list is not None:
                #print('{}: => {} -- {}'.format(action_rounded_date, matching_list, action["data"]["card"]["name"]))
                output_data[action_rounded_date][matching_list].add(action["data"]["card"]["id"])

        return output_data
            
    def getCfdData(self, board_id):
        data = self.fetcher.fetch(board_id)

        lists = data["lists"]
        output_data = self._process(data)

        formatted_data = {}
        for list_ in lists:
            formatted_data[list_.name] = {}
            for date in output_data:
                formatted_data[list_.name][date] = len(output_data[date][list_.name])

        return formatted_data

    def getBurnDownData(self, board_id):
        data = self.fetcher.fetch(board_id)
        return self._process(data)