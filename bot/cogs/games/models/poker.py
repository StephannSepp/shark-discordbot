from enum import Enum

EMOJIS = {
    "SPADE": [
        "<:SpadeA:1190853725091266571>",
        "<:Spade2:1190853703645810818>",
        "<:Spade3:1190853705281568789>",
        "<:Spade4:1190853708095959040>",
        "<:Spade5:1190853880964186142>",
        "<:Spade6:1190853710771929198>",
        "<:Spade7:1190853715054317579>",
        "<:Spade8:1190853718036455495>",
        "<:Spade9:1190853720796299304>",
        "<:Spade10:1190853882532860025>",
        "<:SpadeJ:1190853727968567357>",
        "<:SpadeQ:1190853734729777283>",
        "<:SpadeK:1190853886404210688>",
    ],
    "HEART": [
        "<:HeartA:1190854501486305342>",
        "<:Heart2:1190854481022291969>",
        "<:Heart3:1190854483480170629>",
        "<:Heart4:1190854485195636886>",
        "<:Heart5:1190854555559272519>",
        "<:Heart6:1190854490841169940>",
        "<:Heart7:1190854494238560357>",
        "<:Heart8:1190854496075644948>",
        "<:Heart9:1190854498814537860>",
        "<:Heart10:1190854558738550896>",
        "<:HeartJ:1190854560605024347>",
        "<:HeartQ:1190854508637589524>",
        "<:HeartK:1190854505869348996>",
    ],
    "DIAMOND": [
        "<:DiamondA:1190854471002112082>",
        "<:Diamond2:1190854448730345522>",
        "<:Diamond3:1190854450680692827>",
        "<:Diamond4:1190854453566382100>",
        "<:Diamond5:1190854456192012458>",
        "<:Diamond6:1190854457806831746>",
        "<:Diamond7:1190854459325165678>",
        "<:Diamond8:1190854462739337286>",
        "<:Diamond9:1190854466086391909>",
        "<:Diamond10:1190854468896571433>",
        "<:DiamondJ:1190854473917145149>",
        "<:DiamondQ:1190854478610567199>",
        "<:DiamondK:1190854475519369327>",
    ],
    "CLUB": [
        "<:ClubA:1190853693780787230>",
        "<:Club2:1190853670020067428>",
        "<:Club3:1190853672637308988>",
        "<:Club4:1190853674365358130>",
        "<:Club5:1190853677171347549>",
        "<:Club6:1190853680568741908>",
        "<:Club7:1190853681973837825>",
        "<:Club8:1190853686491095121>",
        "<:Club9:1190853689515200563>",
        "<:Club10:1190853691138383872>",
        "<:ClubJ:1190853695437549598>",
        "<:ClubQ:1190853700525228032>",
        "<:ClubK:1190853698423898142>",
    ],
}


class Suit(Enum):
    SPADE = 4
    HEART = 3
    DIAMOND = 2
    CLUB = 1


class Card:
    is_ace = False
    use_lower_value = False
    is_hidden = False

    def __init__(self, name: str, suit: Suit, value: int, emoji: str):
        self.name = name
        self.suit = suit
        self._value = value
        self.emoji = emoji

    def __str__(self):
        return "<:CardFaceDown:1190853668405248050>" if self.is_hidden else self.emoji

    def __lt__(self, other: "Card"):
        if self.value != other.value:
            return self.value < other.value
        return self.suit.value < other.suit.value

    def __gt__(self, other: "Card"):
        if self.value != other.value:
            return self.value > other.value
        return self.suit.value > other.suit.value

    @property
    def value(self):
        return 1 if self.use_lower_value else self._value


def create_cards_pool():
    card_pool = []
    for suit in Suit:
        for value in range(1, 14):
            match value:
                case 1:
                    name = f"{suit.name} A".title()
                    card = Card(name, suit, 11, EMOJIS[suit.name][value - 1])
                    card.is_ace = True
                case 11:
                    name = f"{suit.name} J".title()
                    card = Card(name, suit, 10, EMOJIS[suit.name][value - 1])
                case 12:
                    name = f"{suit.name} Q".title()
                    card = Card(name, suit, 10, EMOJIS[suit.name][value - 1])
                case 13:
                    name = f"{suit.name} K".title()
                    card = Card(name, suit, 10, EMOJIS[suit.name][value - 1])
                case _:
                    name = f"{suit.name} {value}".title()
                    card = Card(name, suit, value, EMOJIS[suit.name][value - 1])
            card_pool.append(card)
    return card_pool
