
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
            for l in board.get_lists('open'):
                data[l.id] = l.name
            
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

