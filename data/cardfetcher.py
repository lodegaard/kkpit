
class ListCardFetcher:
    def __init__(self, client):
        self.client = client

    def fetch(self, list_id=None):
        if list_id is None:
            return []
            
        l = self.client.get_list(list_id)
        
        data = []
        for card in l.list_cards():
            c = {}
            c['id'] = card.id
            c['name'] = card.name
            c['members'] = card.member_id
            data.append(c)

        return data

