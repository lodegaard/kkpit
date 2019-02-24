import trello
import datetime
from data import cardstatprocessor
from config import api_key, app_token
client = trello.TrelloClient(api_key, token=app_token)

kanban_board_id = '5beebf864359e813be900408'

if __name__ == '__main__':
    p = cardstatprocessor.CardStatsProcessor(client)
    
    data = p.process(kanban_board_id)

    for card in data:
        if len(data[card]["movements"]['Done']) > 0 and data[card]["movements"]['Done'][-1].entry is not None:
            
            days = {}
            for l in data[card]["movements"]:
                if l != 'Done':
                    hours_in_list = 0
                    days[l] = 0
                    for p in data[card]["movements"][l]:
                        if p.entry is not None and p.leave is not None:
                            #print('  entered {} at {}, left at {}'.format(l, p.entry, p.leave))
                            dt = p.leave - p.entry
                            days[l] += dt.days
                            hours_in_list += dt.total_seconds()/60/60
                        elif p.entry is not None:
                            dt = datetime.datetime.today() - p.entry
                            days[l] += dt.days
                            hours_in_list += dt.total_seconds()/60/60

            x = data[card]["movements"]['Done'][-1].entry
            y = sum(days.values())
            print(x, y)
