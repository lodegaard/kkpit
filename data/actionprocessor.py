import copy
import datetime
import math
from collections import OrderedDict
from recordclass import recordclass

Delta = recordclass('Delta', ['entry', 'leave'])

class ActionProcessor:
    fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
    def _process(self, actions, lists):
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


class CfdProcessor(ActionProcessor):
    def __init__(self):
        super().__init__()

    def getCfdData(self, actions, lists):
        ''' Get data for cumulative flow chart based on the actions on the board '''

        output_data = self._process(actions, lists)
        formatted_data = {}
        for l in lists:
            formatted_data[l.name] = {}
            for date in output_data:
                formatted_data[l.name][date] = len(output_data[date][l.name])

        return formatted_data



class BurnDownProcessor(ActionProcessor):

    def getBurnDownData(self, actions, lists):
        ''' Get data for burn-up and burn-down chart based on actions on the bord'''
        data = self._process(actions, lists)

        formatted_data = {}
        for date in data:
            y_sum = 0
            for series in data[date]:
                if series != 'Done':
                    y_sum += len(data[date][series])
            formatted_data[date] = y_sum

        return formatted_data

class BurnUpProcessor(ActionProcessor):

    def getBurnUpData(self, actions, lists):
        ''' Get data for burn-up and burn-down chart based on actions on the bord'''
        data = self._process(actions, lists)

        formatted_data = {}
        for date in data:
            formatted_data[date] = {}
            formatted_data[date]["Done"] = 0
            formatted_data[date]["Work in progress"] = 0
            for series in data[date]:
                if series == 'Done':
                    formatted_data[date]["Done"] += len(data[date][series])
                else:
                    formatted_data[date]["Work in progress"] += len(data[date][series])


        return formatted_data

class CtaProcessor(ActionProcessor):

    def _process(self, actions, lists):
        output_data = {}
        card_movement = {}
        for action in sorted(actions, key=lambda action: datetime.datetime.strptime(action["date"], self.fmt)):
            action_date = datetime.datetime.strptime(action["date"], self.fmt)
            action_type = action["type"]

            action_card = None
            list_in = None
            list_out = None
            if action_type == 'updateCard':
                action_card = action["data"]["card"]
                if 'listBefore' in action["data"].keys() and 'listAfter' in action["data"].keys():
                    list_in = action["data"]["listAfter"]["name"]
                    list_out = action["data"]["listBefore"]["name"]
                    #print('{}: Card {} moved from {} to {}'.format(action_date, action_card["name"], list_out, list_in))

            elif action_type == 'createCard' and 'name' in action["data"]["list"]:
                action_card = action["data"]["card"]
                list_in = action["data"]["list"]["name"]
                #print('{}: Card {} created in {}'.format(action_date, action_card["name"], list_in))

            # Create the entry for this card
            if action_card is not None and action_card["id"] not in card_movement.keys():
                card_movement[action_card["id"]] = {}
                card_movement[action_card["id"]]["info"] = action_card["name"]
                card_movement[action_card["id"]]["movements"] = {}
                for l in lists:
                    card_movement[action_card["id"]]["movements"][l.name] = []

            if action_card is not None:
                if list_out is not None and len(card_movement[action_card["id"]]["movements"][list_out]) > 0:
                    card_movement[action_card["id"]]["movements"][list_out][-1].leave = action_date
                if list_in is not None:
                    card_movement[action_card["id"]]["movements"][list_in].append(Delta(action_date, None))
        
        return card_movement

    def getCtaData(self, actions, lists):
        ''' Get data for cycle time analysis based on actions on the board '''
        data = self._process(actions, lists)

        formatted_data = {}
        for card in data:
            if len(data[card]["movements"]['Done']) > 0 and data[card]["movements"]['Done'][-1].entry is not None:
                days = {}
                for l in data[card]["movements"]:
                    if l != 'Done':
                        days[l] = 0
                        for p in data[card]["movements"][l]:
                            if p.entry is not None and p.leave is not None:
                                dt = p.leave - p.entry
                                days[l] += dt.days
                            elif p.entry is not None:
                                dt = datetime.datetime.today() - p.entry
                                days[l] += dt.days
                
                days['Doing'] += 1
                formatted_data[data[card]["movements"]['Done'][-1].entry] = {}
                formatted_data[data[card]["movements"]['Done'][-1].entry]["Lead"] = sum(days.values())
                formatted_data[data[card]["movements"]['Done'][-1].entry]["Cycle"] = sum([d for l, d in days.items() if l != 'To do'])
                
                details = '<br>'.join(['{}: {} days'.format(l, d) for l, d in days.items()])
                formatted_data[data[card]["movements"]['Done'][-1].entry]["Details"] = '{}<br>{}'.format(data[card]["info"], details)

        return formatted_data
        
    def getCmaData(self, cta_data):
        cma = {}
        prev_date = None
        for i,v in sorted(enumerate(cta_data), key=lambda k:k[1]):
            cma_prev = cma[prev_date] if prev_date is not None else 0
            cma[v] = (cta_data[v]["Cycle"]+len(cma)*cma_prev)/(len(cma)+1)
            prev_date = v

        return cma

    def getPercentiles(self, cta_data, vals=[]):
        percentiles = {}
        processed_values = []
        for dt in sorted(cta_data.keys()):
            percentiles[dt] = {}
            processed_values.append(cta_data[dt]["Cycle"])
            tmp = sorted(processed_values)
            for v in vals:
                i = math.floor((v/100)*len(tmp))
                percentiles[dt][v] = tmp[i]

        return percentiles