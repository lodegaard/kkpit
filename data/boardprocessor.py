class BoardListProcessor:
        
    def getCardsPerListData(self, lists):
        output_data = {}
        for l,cards in lists.items():
            output_data[l] = len(cards)

        return output_data

    def getCardsPerMemberData(self, lists, members):
        
        output_data = {}

        output_data = {}
        for l,cards in lists.items():
            if l != 'Done':
                output_data[l] = {}
                for card in cards:
                    if len(card["members"]) > 0:
                        if not members[card["members"][0]] in output_data[l].keys():
                            output_data[l][members[card["members"][0]]] = []
                        output_data[l][members[card["members"][0]]].append(card["id"])
        
        return output_data