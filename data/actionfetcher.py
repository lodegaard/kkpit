import datetime


class ActionFetcher:
    list_filter = 'open'
    action_filter = 'createCard,updateCard,updateList,moveCardToBoard,moveCardFromBoard,convertToCardFromCheckItem'
    action_limit = 1000

    def __init__(self, client):
        self.client = client

    def fetch(self, board_id=None):
        data = {}
        if board_id is not None:
            board = self.client.get_board(board_id)
            data["lists"] = board.get_lists(self.list_filter)
            data["actions"] = self._get_all_actions(board)

        return data

    def fetch_raw(self, board_id=None):
        data = {}
        if board_id is not None:
            board = self.client.get_board(board_id)
            data = self._get_all_actions(board)

        return data

    def _get_all_actions(self, board, start=None, end=None):
        since = start if start is not None else datetime.datetime(2019, 1, 1)
        before = end if end is not None else datetime.datetime.today() + datetime.timedelta(days=1)

        actions = board.fetch_actions(self.action_filter, self.action_limit, before, since)

        return actions