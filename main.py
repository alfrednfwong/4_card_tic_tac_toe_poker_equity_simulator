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

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return self.name()

    def name(self):
        # as a function rather than an attribute because in the Deck functions, when a card has to be deleted a new
        # copy of the deck has to be made. Not having to copy the Card.name saves some CPU time.
        return RANK_NAMES[self.rank] + SUIT_NAMES[self.suit]


class Deck:
    """
    A deck. Attribute Deck.cards contain the cards in the deck in an array.
    """

    def __init__(self, num_ranks=13, num_suits=4):
        '''
        :param num_ranks: number of ranks in the deck of this game. Default to 13
        :param num_suits: number of suits in the deck of this game. Default to 4
        :return: a Deck object, with the attribute Deck.cards containing Card objects newly created.
        '''
        self.cards = np.empty([num_ranks * num_suits], dtype=Card)
        card_index = 0
        for i in range(1, num_suits + 1):
            for j in range(15 - num_ranks, 15):
                self.cards[card_index] = Card(j, i)
                card_index += 1

    def __repr__(self):
        return "Deck object with {} Card objects".format(len(self.cards))

    def pick(self, card_name_to_pick):
        """Takes the named Card object out of the deck and returns it. The Card object will be removed from the deck."""
        for i in range(len(self.cards)):
            if self.cards[i].name() == card_name_to_pick:
                result = self.cards[i]
                self.cards = np.delete(self.cards, i)
                return result
        raise Exception("Card picked not in deck", card_name_to_pick)

    def deal(self):
        """Takes a random Card object out of the deck and returns it. The Card object will be removed from the deck."""
        if len(self.cards) > 0:
            card_key = random.choice(range(len(self.cards)))
            result = self.cards[card_key]
            self.cards = np.delete(self.cards, card_key)
            return result
        else:
            raise Exception("No more cards in deck")


class Board:
    """
    A board containing a 3x3 grid of cards. Card objects are stored in Board.board_cards as a numpy array.
    """

    def __init__(self, board_cards=[[None, None, None], [None, None, None], [None, None, None]]):
        self.board_cards = np.array(board_cards)

    def __repr__(self):
        return "Board: \n" + str(self.board_cards)

    def generate_board_combos(self):
        """
        :return: An array of 8 three-Card-object-combinations that lie on straight lines on the board.
        """
        self.board_combos = np.empty((8, 3), dtype=Card)
        # horizontals
        self.board_combos[0:3] = self.board_cards
        # verticals
        self.board_combos[3:6] = self.board_cards.transpose()
        # diagonals
        self.board_combos[6] = np.diag(self.board_cards)
        self.board_combos[7] = np.diag(np.fliplr(self.board_cards))


class Player:
    """
    Player object containing hole cards they hold in the attribute Player.hole_cards. The method
    Player.generate_showdown_hand(self, board) creates the attribute Player.showdown_hand, which is a Hand object that
    the player can best make on the board.
    """

    def __init__(self, player_num, hole_cards = [None, None, None, None]):
        self.hole_cards = np.array(hole_cards)
        self.player_num = player_num

    def __repr__(self):
        return "Player {} holding {}".format(self.player_num, self.hole_cards)

    def generate_hole_cards_combos(self):
        """
        Create an attribute hole_cards_combos, an array that contains all two-card-combos the player can make with his
        hole cards.
        """
        self.hole_cards_combos = np.empty(NUM_HOLE_CARDS * (NUM_HOLE_CARDS - 1) // 2, dtype=Card)
        i = 0
        for combo in combinations(self.hole_cards, 2):
            self.hole_cards_combos[i] = np.array(combo)
            i += 1

    def generate_showdown_hand(self, board):
        '''
        :param board: a Board object
        Creates an attribute showdown_hand, a hand object representing the best hand the player can make on the given
        board
        '''

        best_hand = None
        for board_combo in board.board_combos:
            for hole_cards_combo in self.hole_cards_combos:
                current_hand = Hand(np.concatenate((hole_cards_combo, board_combo)))
                if best_hand == None or current_hand.compare(best_hand) == 1:
                    best_hand = current_hand
        self.showdown_hand = best_hand


class Hand:
    """
    An object representing a 5-card-poker-hand. Hand.cards contain an array of 5 Card objects.
    Hand.hand_ranking contains an array of values that can be compared with one another, from the first element to the
    last, to determine the higher hand.
    """

    def __init__(self, cards):
        self.cards = cards
        self.get_hand_ranking()

    def __repr__(self):
        return self.cards

    def get_hand_ranking(self):
        '''
        Creates an attribute Hand.hand_ranking which is an array of 6 values. [0] is the hand ranking, [1] to [5] are
        the card rankings, starting from the rank that needs to be compared first, in that hand rank category.
        E.g. for a hand JJ337, the first rank is J, the second is 3 and the third is 7. The unused values, like the
        third onwards in this case, will be 0

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

        self.hand_ranking = np.zeros(6, dtype=np.int8)
        cards_ranks = np.empty(5, dtype=np.int8)
        for i in range(5):
            cards_ranks[i] = self.cards[i].rank
        # create a 2d array, with first item of each element being ranks and second being the number of cards in the
        # ranks. Sorted first by the frequency (second item) and then the rank (first item)
        ordered_ranks_counts = np.array(
            sorted(collections.Counter(cards_ranks).items(), key=lambda item: (-item[1], -item[0]))
        )

        # check for flush possibility first so that we can use it for the straightflush check
        is_flush = True
        for i in range(4):
            if self.cards[i].suit != self.cards[i + 1].suit:
                is_flush = False
                break

        # same reason, check for straight possibility. A wheel is 5432A in a regular deck, with the ace playing as a 1.
        # but in some short deck games, like with the 2s - 5s removed, 9876A is a legal wheel.
        is_straight = False
        # check if there are 5 distinct ranks first
        if len(ordered_ranks_counts) == 5:
            # check for non-wheel straights
            if ordered_ranks_counts[0, 0] - ordered_ranks_counts[4, 0] == 4:
                is_straight = True
                straight_rank = ordered_ranks_counts[0, 0]
            # check for wheels
            elif WHEEL_RANKS is not None and np.array_equal(ordered_ranks_counts[:, 0], WHEEL_RANKS):
                is_straight = True
                # if it is a wheel, the ace plays as a 1 so the highest rank in the straight is the second element of
                # the ordered_ranks_counts
                straight_rank = ordered_ranks_counts[1, 0]

        # check straightflush, flush and straight
        if is_flush:
            if is_straight:
                # Straightflush. Royalflush is the same thing with a rank of 14
                self.hand_ranking[0:2] = 9, straight_rank
                return
            else:
                # Flush. Quads and fullhouse not possible with a flush there.
                self.hand_ranking[0] = 6
                self.hand_ranking[1:6] = ordered_ranks_counts[0:5, 0]
                return

        if is_straight:
            # Straight. Quads and fullhouse not possible.
            self.hand_ranking[0:2] = 5, straight_rank
            return

        # check quads
        if ordered_ranks_counts[0, 1] == 4:
            self.hand_ranking[0] = 8
            self.hand_ranking[1:3] = ordered_ranks_counts[0:2, 0]
            return

        # check fullhouse and 3 of a kind
        if ordered_ranks_counts[0, 1] == 3:
            if ordered_ranks_counts[1, 1] == 2:
                # fullhouse
                self.hand_ranking[0] = 7
                self.hand_ranking[1:3] = ordered_ranks_counts[0:2, 0]
            else:
                # 3 of a kind.
                self.hand_ranking[0] = 4
                self.hand_ranking[1:4] = ordered_ranks_counts[0:3, 0]
            return

        # check two pair and one pair
        if ordered_ranks_counts[0, 1] == 2:
            if ordered_ranks_counts[1, 1] == 2:
                # Two pair.
                self.hand_ranking[0] = 3
                self.hand_ranking[1:4] = ordered_ranks_counts[0:3, 0]
            else:
                # One pair.
                self.hand_ranking[0] = 2
                self.hand_ranking[1:5] = ordered_ranks_counts[0:4, 0]
        else:
            # None of the above, so high card it is.
            self.hand_ranking[0] = 1
            self.hand_ranking[1:6] = ordered_ranks_counts[0:5, 0]
        return

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
        self.players = np.empty(len(hole_cards_input), dtype=Player)
        self.board = Board()
        self.num_trials = num_trials
        # create players and their hole cards
        for i in range(len(hole_cards_input)):
            self.players[i] = Player(player_num=i + 1)
            for j in range(NUM_HOLE_CARDS):
                if hole_cards_input[i, j] != "*":
                    self.players[i].hole_cards[j] = self.deck.pick(hole_cards_input[i, j])
                else:
                    self.players[i].hole_cards[j] = None
        # put the cards on the board
        for i in range(3):
            for j in range(3):
                if board_input[i, j] != "*":
                    self.board.board_cards[i, j] = self.deck.pick(board_input[i, j])
        # take away the dead cards
        for card_name in dead_cards_input:
            self.deck.pick(card_name)

    def answer(self):
        """
        :return: Simulation results in an array, each element is the equity of a player, ordered by the player number.
        The index for each player is [Player.player_num - 1]
        """
        results = np.zeros(len(self.players), dtype=float)
        for i in range(self.num_trials):
            trial_winners = Trial(players=self.players, board=self.board, deck=self.deck).run()
            for player in trial_winners:
                # if there are 2 winners in a hand, each of them have 50% equity, thus the 1 / len(trial_winners)
                # index - 1 because our player_nums start from 1, python counts start from 0
                results[player.player_num - 1] += 1 / len(trial_winners)
        print("###########################")
        print("Results after {} trials:\n".format(self.num_trials))
        for i in range(len(results)):
            print("    Player {}: {}%".format(i + 1, str(100 * results[i] / self.num_trials)))
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
        :return: An array of Player objects who have won in this trial.
        """

        # deal the (remainder of) the board
        for i in range(3):
            for j in range(3):
                if self.board.board_cards[i, j] is None:
                    self.board.board_cards[i, j] = self.deck.deal()
        self.board.generate_board_combos()

        # deal to players, if they have None in their hole_cards
        for player in self.players:
            for i in range(len(player.hole_cards)):
                if player.hole_cards[i] is None:
                    player.hole_cards[i] = self.deck.deal()
            player.generate_hole_cards_combos()
            player.generate_showdown_hand(self.board)

        # showdown
        winning_players = np.array([self.players[0]])
        for player in self.players[1:]:
            compare_result = player.showdown_hand.compare(winning_players[0].showdown_hand)
            if compare_result == 1:
                winning_players = np.array([player])
            # in case of a tie
            elif compare_result == 0:
                winning_players = np.append(winning_players, player)
        return winning_players


def card_input_validate(card_names, previous_cards, num_cards_required=None):
    """
    To validate user input of cards, preventing wrong number of cards, cards not recognized in our notation, and
    duplicated cards.
    Called by prompt_user()
    :param card_names: an array of strings, for the card names.
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
                 hole_cards_input: an array of strings for the names of the hole cards.
                 board_input: a 2d array of strings, for the names of the board cards in each row.
                 dead_cards_input: an array of strings, for the names of dead cards, if any.
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
    hole_cards_input = np.empty([num_players, NUM_HOLE_CARDS], dtype="<U2")
    print("\nFormat e.g.: 'As' for ace of spades, '5c' for 5 of clubs, 'Th' for 10(ten) of hearts. Without the quotes.")
    print("Use * for an unknown or undealt card.")
    print("Separate each card with a comma.\n")
    for i in range(num_players):
        while True:
            card_names = np.array(input("Player {} hole cards: \n".format(str(i + 1))).replace(" ", "").split(","))
            if card_input_validate(card_names, previous_cards, NUM_HOLE_CARDS):
                previous_cards.update(set(card_names))
                hole_cards_input[i] = card_names
                break

    board_input = np.empty([3, 3], dtype="<U2")
    for i in range(3):
        while True:
            card_names = np.array(input("Board row {}:\n".format(str(i + 1))).replace(" ", "").split(","))
            if card_input_validate(card_names, previous_cards, 3):
                previous_cards.update(set(card_names))
                board_input[i] = card_names
                break

    while True:
        card_names = np.array(input("Dead cards: \n").replace(" ", "").split(","))
        # even if the user hit enter without anything, card_names will still get [''] after the split.
        # putting that into the validate function won't work as it will be counted as one unrecognized card.
        if len(card_names) == 1 and card_names[0] == "":
            dead_cards_input = np.empty([0], dtype="<U2")
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
# The ranks of a wheel allowed in the game, with A being entered as a 14 (but will count as a 1 when comparing hands)
# This is used in case of short deck games allowing hands like 9876A being a legal wheel.
# Also applies to straight flushes.
# Assign a value of None if wheels not allowed.
WHEEL_RANKS = np.array([14, 5, 4, 3, 2])

while True:
    hole_cards_input, board_input, dead_cards_input, num_trials = prompt_user()
    q1 = Question(hole_cards_input, board_input, dead_cards_input, num_trials)
    q1.answer()

