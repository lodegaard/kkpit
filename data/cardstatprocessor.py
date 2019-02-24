import datetime
from recordclass import recordclass
from .actionfetcher import ActionFetcher

Delta = recordclass('Delta', ['entry', 'leave'])

'''
To build cycle time analysis:

x-axis: time card was put in 'Done'
y-axis: sum of time spent in 'Doing', 'For review' and 'On hold'

Time spent in a list:
Each card has a array of lists it has spent time in
Each of the lists has an array of entry and leave times
for example:
    {
        'Design application': {
            'To do': [
                Delta(entry=date(), leave=date()),
                Delta(entry=date(), leave=date()),
            ],
            'Doing': [
                Delta(entry=date(), leave=date()),
            ],
            'For review': [
                Delta(entry=date(), leave=date()),
            ],
            'On hold': [
                Delta(entry=date(), leave=date()),
            ],
            'Done': [
                Delta(entry=date(), leave=None),
            ]
        }
    }

for each time a card was moved from one list to another
  entry for the after list is the event time
  leave time for the before list is the event time
 
'''

class CardStatsProcessor:
    fmt = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, client):
        self.client = client
        self.fetcher = ActionFetcher(client)

    def process(self, board_id):
        data = self.fetcher.fetch(board_id)

        actions = data["actions"]
        lists = data["lists"]

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

            

            
    def getCtaData(self, board_id):
        board = self.client.get_board(board_id)
        lists = board.get_lists('open')

        output_data = []
        for l in lists:
            if l.name == 'Done':
                for card in l.list_cards():
                    output_data.append(card.name)

        return output_data

