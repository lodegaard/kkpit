class BoardListProcessor:
        
    def getCardsPerListData(self, lists):
        output_data = {}
        for l in lists:
            output_data[l.name] = len(l.list_cards())

        return output_data

    def getCardsPerMemberData(self, lists, members):
        
        output_data = {}

        output_data = {}
        for l in lists:
            if l.name != 'Done':
                output_data[l.name] = {}
                for card in l.list_cards():
                    if len(card.member_id) > 0:
                        if not members[card.member_id[0]] in output_data[l.name].keys():
                            output_data[l.name][members[card.member_id[0]]] = []
                        output_data[l.name][members[card.member_id[0]]].append(card.id)
        
        return output_data