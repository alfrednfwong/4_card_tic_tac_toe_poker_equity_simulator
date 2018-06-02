# This is an equity calculator for the poker variant 4 Card Tic-tac-toe.
# Each player has 4 hole cards. The board will form a 3x3 square, and players can make a final hand with any of their
#     two hole cards plus any 3 cards on the board that forms a straight line, vertical, horizontal or diagonal.
# On the flop the 4 corners of the board will be dealt, and on the turn, the 4 sides, with the river being the center
#     card alone.

import collections
import numpy as np
import copy
import random
from itertools import combinations


class Card:
    """
    A card. Rank and suits follow the global variable RANK_NAMES and SUIT_NAMES. Name takes a upper case rank followed
    by a lower case suit, e.g. As, Th, 9d, 4c. The rank 10 (Ten) should be called T.
    Can be created in Deck().__init__ .
    """

    def __init__(self, name, rank, suit):
        self.rank = rank
        self.suit = suit
        self.name = name

    def __repr__(self):
        return "Card " + self.name


class Deck:
    """
    A deck. Attribute Deck.cards contain the cards in the deck in a dictionary, with the key being the card names and
    values being the card objects.
    """

    def __init__(self, num_ranks=13, num_suits=4):
        '''
        :param num_ranks: number of ranks in the deck of this game. Default to 13
        :param num_suits: number of suits in the deck of this game. Default to 4
        :return: a Deck object, with the attribute Deck.cards containg Card objects newly created.
        '''
        cards = {}
        for i in range(1, num_suits + 1):
            for j in range(15 - num_ranks, 15):
                card_name = RANK_NAMES[j] + SUIT_NAMES[i]
                cards[card_name] = Card(card_name, j, i)
        self.cards = cards

    def __repr__(self):
        return "Deck object with {} Card objects".format(len(self.cards))

    def pick(self, card_name_to_pick):
        """Takes the named Card object out of the deck and returns it. The Card object will be removed from the deck."""
        if card_name_to_pick in self.cards:
            return self.cards.pop(card_name_to_pick)
        else:
            raise Exception("Card picked not in deck", card_name_to_pick)

    def deal(self):
        """Takes a random Card object out of the deck and returns it. The Card object will be removed from the deck."""
        if self.cards:
            card_key = random.choice(list(self.cards))
            return self.cards.pop(card_key)
        else:
            raise Exception("No more cards in deck")


class Board:
    """
    A board containing a 3x3 grid of cards. Card objects are stored in Board.board_cards as a numpy array.
    """

    def __init__(self, board_cards=[[None, None, None], [None, None, None], [None, None, None]]):
        self.board_cards = np.array(board_cards)

    def __repr__(self):
        to_print = ["Board: "]
        for row in self.board_cards:
            for card in row:
                if card:
                    to_print.append(card.name)
                else:
                    to_print.append("*")
        return " ".join(to_print)

    def generate_board_combos(self):
        """
        :return: A list of 8 three-Card-object-combinations that lie on straight lines on the board.
        """
        board_combos = []
        # horizontals and verticals
        for i in range(3):
            board_combos.append(list(self.board_cards[i, 0:3]))
            board_combos.append(list(self.board_cards[0:3, i]))
        # diagonals
        board_combos.append([self.board_cards[0, 0], self.board_cards[1, 1], self.board_cards[2, 2]])
        board_combos.append([self.board_cards[2, 0], self.board_cards[1, 1], self.board_cards[0, 2]])
        self.board_combos = board_combos


class Player:
    """
    Player object containing hole cards they hold in the attribute Player.hole_cards. The method
    Player.generate_showdown_hand(self, board) creates the attribute Player.showdown_hand, which is a Hand object that
    the player can best make on the board.
    """

    def __init__(self, player_num, hole_cards=[None, None, None, None]):
        self.hole_cards = hole_cards
        self.player_num = player_num

    def __repr__(self):
        to_print = ["Player ", str(self.player_num), " holding "]
        for card in self.hole_cards:
            if card:
                to_print.append(card.name)
            else:
                to_print.append("*")
        return " ".join(to_print)

    def generate_hole_cards_combos(self):
        """
        Create an attribute hole_cards.combos, a list that contains all two-card-combos the player can make with his
        hole cards.
        """
        self.hole_cards_combos = []
        for combo in combinations(self.hole_cards, 2):
            self.hole_cards_combos.append(list(combo))

    def generate_showdown_hand(self, board):
        '''
        :param board: a Board object
        Creates an attribute showdown_hand, a hand object representing the best hand the player can make on the given
        board
        '''

        best_hand = None
        for board_combo in board.board_combos:
            for hole_cards_combo in self.hole_cards_combos:
                current_hand = Hand(hole_cards_combo + board_combo)
                if best_hand == None or current_hand.compare(best_hand) == 1:
                    best_hand = current_hand
        self.showdown_hand = best_hand


class Hand:
    """
    An object representing a 5-card-poker-hand. Hand.cards contain 5 Card objects. Hand.hand_ranking contains a list of
    values that can be compared with one another, from the first element to the last, to determine the higher hand.
    """

    def __init__(self, cards):
        self.cards = cards
        self.hand_ranking = self.get_hand_ranking()

    def get_hand_ranking(self):
        '''
        Creates an attribute Hand.hand_ranking which is a list of 2 - 6 values. [0] is the hand ranking, [1] to [5] are
        the card rankings, starting from the
        rank that needs to be compared first, in that hand rank category. E.g. for a hand JJ337, the first rank is
        J, the second is 3 and the third is 7.

        Hand ranking values
        1 - High card (5 card ranks)
        2 - One pair (4 card ranks, with the rank of the pair going first)
        3 - Two pair (3 card ranks, with the higher of the pair ranks going first, the other pair's second)
        4 - Three of a kind (3 card ranks, with the rank of the trips going first)
        5 - Straight (1 card rank, of the top card of the straight)
        6 - Flush (5 card ranks)
        7 - Fullhouse (2 card ranks, with the rank of the trips going first)
        8 - Four of a kind (2 card ranks, with the rank of the quads going first)
        9 - Straightflush / royalflush (1 card rank, of the top card of the straight/royalflush)
        '''
        cards_ranks = []
        cards_suits = set()
        for card in self.cards:
            cards_ranks.append(card.rank)
            cards_suits.add(card.suit)
        # sort the cards' ranks from high to low
        cards_ranks = sorted(cards_ranks, reverse=True)
        # created an ordered dict, with keys being the ranks and the values being the number of cards in the ranks.
        # sorted first by the values and then they key
        ordered_ranks_counts = sorted(collections.Counter(cards_ranks).items(),
                                      key=lambda item: (-item[1], -item[0]))

        # check for flush possibility first so that we can use it for the straightflush check
        if len(cards_suits) == 1:
            is_flush = True
        else:
            is_flush = False

        # same reason, check for straight possibility. A wheel is 5432A in a regular deck, with the ace playing as a 1.
        # but in some short deck games, like with the 2s - 5s removed, 9876A is a legal wheel.
        min_rank = 15 - DECK_NUM_RANKS
        # check for wheel first
        if WHEEL_LEGAL and cards_ranks == [14, min_rank + 3, min_rank + 2, min_rank + 1, min_rank]:
            is_straight = True
            straight_rank = min_rank + 3
        # check for non-wheel straights
        elif (len(set(cards_ranks)) == 5) and (cards_ranks[0] - cards_ranks[4] == 4):
            is_straight = True
            straight_rank = cards_ranks[0]
        else:
            is_straight = False

        # check straightflush
        if is_straight and is_flush:
            return [9, straight_rank]

        # check quads
        if ordered_ranks_counts[0][1] == 4:
            return [8, ordered_ranks_counts[0][0], ordered_ranks_counts[1][0]]

        # check fullhouse
        if ordered_ranks_counts[0][1] == 3 and ordered_ranks_counts[1][1] == 2:
            return [7, ordered_ranks_counts[0][0], ordered_ranks_counts[1][0]]

        if is_flush:
            return [6] + cards_ranks

        if is_straight:
            return [5, straight_rank]

        # check three of a kind
        if ordered_ranks_counts[0][1] == 3:
            return [4, ordered_ranks_counts[0][0], ordered_ranks_counts[1][0], ordered_ranks_counts[2][0]]

        # check two pair
        if ordered_ranks_counts[0][1] == 2 and ordered_ranks_counts[1][1] == 2:
            return [3, ordered_ranks_counts[0][0], ordered_ranks_counts[1][0], ordered_ranks_counts[2][0]]

        # check one pair
        if ordered_ranks_counts[0][1] == 2:
            return [2, ordered_ranks_counts[0][0], ordered_ranks_counts[1][0], ordered_ranks_counts[2][0],
                    ordered_ranks_counts[3][0]]

        # none of the above, so high card it is.
        return [1] + cards_ranks

    def compare(self, hand_to_beat):
        """
        Compares the Hand object with another Hand object. Returns 1 if the self object is a higher hand, -1 if lower,
        and 0 for a tie.
        """
        for i in range(len(self.hand_ranking)):
            if self.hand_ranking[i] > hand_to_beat.hand_ranking[i]:
                return 1
            if self.hand_ranking[i] < hand_to_beat.hand_ranking[i]:
                return -1
        return 0


class Question:
    """
    An object representing an equity (winning probability) question by the user: If player A holds this and player B
    holds that on this board, what is the equity of each of the players? Do this many trials in a Monte Carlo
    simulation to find out.
    Method Question.answer() prints and returns the results.
    """

    def __init__(self, hole_cards_input, board_input, dead_cards_input, num_trials):
        self.deck = Deck(num_ranks=DECK_NUM_RANKS, num_suits=DECK_NUM_SUITS)
        self.players = []
        self.board = Board()
        self.num_trials = num_trials
        # create players and their hole cards
        for i in range(len(hole_cards_input)):
            hole_cards = []
            for card_name in hole_cards_input[i]:
                if card_name == "*":
                    hole_cards.append(None)
                else:
                    hole_cards.append(self.deck.pick(card_name))
            self.players.append(Player(player_num=i + 1, hole_cards=hole_cards))
        # put the cards on the board
        for i in range(3):
            for j in range(3):
                if board_input[i][j] != "*":
                    self.board.board_cards[i, j] = self.deck.pick(board_input[i][j])
        # take away the dead cards
        for card_name in dead_cards_input:
            self.deck.pick(card_name)

    def answer(self):
        """
        :return: Simulation results in a dictionary, with player_num being the keys and their equities being the values.
        Also prints the results.
        """
        results = {}
        for player in self.players:
            results[player.player_num] = 0
        for i in range(self.num_trials):
            trial_winners = Trial(players=self.players, board=self.board, deck=self.deck).run()
            for player in trial_winners:
                # if there are 2 winners in a hand, each of them have 50% equity, thus the 1 / len(trial_winners)
                results[player.player_num] += 1 / len(trial_winners)
        print("###########################")
        print("Results after {} trials:\n".format(self.num_trials))
        for elem in results:
            print("    Player {}: {}%".format(elem, str(100 * results[elem] / self.num_trials)))
        print("###########################\n\n")
        return results


class Trial:
    """
    A single trial of the Monte Carlo simulation. Method Trial.run() returns the result.
    """

    def __init__(self, players, board, deck):
        # deepcopy from the arguments so that the changes done in this trial would not affect other trials.
        self.players = copy.deepcopy(players)
        self.board = copy.deepcopy(board)
        self.deck = copy.deepcopy(deck)

    def run(self):
        """
        :return: A list of Player objects who have won in this trial.
        """

        # deal the (remainder of) the board
        for i in range(3):
            for j in range(3):
                if self.board.board_cards[i, j] is None:
                    self.board.board_cards[i, j] = self.deck.deal()
        self.board.generate_board_combos()

        # deal to players, if they have * in their hole cards input.
        for player in self.players:
            for i in range(len(player.hole_cards)):
                if player.hole_cards[i] is None:
                    player.hole_cards[i] = self.deck.deal()
            player.generate_hole_cards_combos()
            player.generate_showdown_hand(self.board)

        # showdown
        winning_players = [self.players[0]]
        for player in self.players[1:]:
            compare_result = player.showdown_hand.compare(winning_players[0].showdown_hand)
            if compare_result == 1:
                winning_players = [player]
            # in case of a tie
            elif compare_result == 0:
                winning_players.append(player)
        return winning_players


def card_input_validate(card_names, previous_cards, num_cards_required=None):
    """
    To validate user input of cards, preventing wrong number of cards, cards not recognized in our notation, and
    duplicated cards.
    Called by prompt_user()
    :param card_names: a list of strings, for the card names.
    :param previous_cards: a set of strings, for the card names previously entered, to check for duplicates.
    :param num_cards_required: the correct number of cards in card_names.
    :return: boolean. True if the input is OK
    """
    if num_cards_required is not None and len(card_names) != num_cards_required:
        print("Wrong number of cards.")
        return False
    for card_name in card_names:
        if card_name == "*":
            pass
        elif len(card_name) == 2 and card_name[0] in RANK_NAMES.values() and card_name[1] in SUIT_NAMES.values():
            pass
        else:
            print(card_name, " not recognized.")
            return False
        if card_name in previous_cards and card_name != "*":
            print(card_name + " appearing more than once.")
            return False
        previous_cards.update(card_name)
    return True


def prompt_user():
    """
    Prompts the user for inputs.
    :return: A tuple containing:
                 hole_cards_input: a list of strings for the names of the hole cards.
                 board_input: a list of list of strings, for the names of the board cards in each row.
                 dead_cards_input: a list of strings, for the names of dead cards, if any.
                 num_trials: the number of Monte Carlo trials to run.
    """
    while True:
        try:
            num_players = int(input("Number of players (2-10)? "))
        except:
            print("Not a valid number")
        else:
            if num_players > 1 and num_players < 11:
                break
            else:
                print("Not a valid number")

    # previous_cards to record all card names entered for card_input_validate() to check for duplicates
    previous_cards = set()
    hole_cards_input = []
    print("\nFormat e.g.: 'As' for ace of spades, '5c' for 5 of clubs, 'Th' for 10(ten) of hearts. Without the quotes.")
    print("Use * for an unknown or undealt card.")
    print("Separate each card with a comma.\n")
    for i in range(num_players):
        while True:
            card_names = input("Player {} hole cards: ".format(str(i + 1))).replace(" ", "").split(",")
            if card_input_validate(card_names, previous_cards, NUM_HOLE_CARDS):
                previous_cards.update(set(card_names))
                hole_cards_input.append(card_names)
                break

    board_input = []
    for i in range(3):
        while True:
            card_names = input("Board row {}:".format(str(i + 1))).replace(" ", "").split(",")
            if card_input_validate(card_names, previous_cards, 3):
                previous_cards.update(set(card_names))
                board_input.append(card_names)
            break

    while True:
        card_names = input("Dead cards: ").replace(" ", "").split(",")
        # even if the user hit enter without anything, card_names will still get [''] after the split.
        # putting that into the validate function won't work as it will be counted as one unrecognized card.
        if card_names == ['']:
            dead_cards_input = []
            break
        elif card_input_validate(card_names, previous_cards, None):
            dead_cards_input = card_names
            break

    while True:
        try:
            num_trials = int(input("Number of trials? "))
        except:
            print("Not a valid number")
        else:
            if num_trials > 0:
                break
            else:
                print("Not a valid number")

    return hole_cards_input, board_input, dead_cards_input, num_trials


RANK_NAMES = {14: "A", 13: "K", 12: "Q", 11: "J", 10: "T", 9: "9", 8: "8", 7: "7", 6: "6", 5: "5", 4: "4", 3: "3",
              2: "2"}
SUIT_NAMES = {4: "s", 3: "h", 2: "d", 1: "c"}
DECK_NUM_RANKS = 13
DECK_NUM_SUITS = 4
NUM_HOLE_CARDS = 4
WHEEL_LEGAL = True


while True:
    hole_cards_input, board_input, dead_cards_input, num_trials = prompt_user()
    q1 = Question(hole_cards_input, board_input, dead_cards_input, num_trials)
    q1.answer()

