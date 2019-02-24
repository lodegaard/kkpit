
class BoardListFetcher:
    def __init__(self, client):
        self.client = client

    def fetch(self, board_id=None):
        data = {}
        if board_id is not None:
            board = self.client.get_board(board_id)
            lists = board.get_lists('open')
            for list_ in lists:
                data[list_.name] = list_.list_cards()
            
        return data

    def fetch_raw(self, board_id=None):
        data = {}
        if board_id is not None:
            board = self.client.get_board(board_id)
            lists = board.get_lists('open')
            for l in lists:
                data[l.name] = []
                for card in l.list_cards():
                    data[l.name].append(card)
            
        return data

    

class BoardMemberFetcher:
    def __init__(self, client):
        self.client = client

    def fetch(self, board_id=None):
        data = {}
        if board_id is not None:
            board = self.client.get_board(board_id)
            members = board.all_members()
            for member in members:
                data[member.id] = member.full_name
            
        return data

class BoardListProcessor:
    def __init__(self, client):
        self.client = client
        self.fetcher = BoardListFetcher(client)

    def getCardsPerListData(self, board_id):
        data = self.fetcher.fetch(board_id)

        output_data = {}
        for list_ in data:
            output_data[list_] = len(data[list_])

        return output_data

    def getCardsPerMemberData(self, board_id):
        board = self.client.get_board(board_id)
        members = board.all_members()
        
        data = self.fetcher.fetch(board_id)
        
        output_data = {}
        member_map = {}
        for member in members:
            member_map[member.id] = member.full_name
            output_data[member.full_name] = []

        output_data = {}
        for list_ in data:
            if list_ != 'Done':
                output_data[list_] = {}
                for card in data[list_]:
                    if len(card.member_id) > 0:
                        if not member_map[card.member_id[0]] in output_data[list_].keys():
                            output_data[list_][member_map[card.member_id[0]]] = []
                        output_data[list_][member_map[card.member_id[0]]].append(card.id)
        
        return output_data
