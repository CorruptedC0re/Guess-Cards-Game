import pygame
import pygame_menu
import os
import random
from threading import Timer
from typing import Tuple, Any


def change_difficulty(selected: Tuple, value: Any) -> None:
    global difficulty
    difficulty = selected[1]


def start():
    global p_one_name, p_two_name
    Game(p_one_name.get_value(), p_two_name.get_value(), WINDOW, difficulty)


def close():
    quit()


WIDTH = 800
HEIGHT = 800
difficulty = 0
name_1 = "Player_1"
name_2 = "Player_2"
pygame.init()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

menu = pygame_menu.Menu("Guess the Cards!", 800, 800, theme=pygame_menu.themes.THEME_BLUE)
p_one_name = menu.add.text_input("Player_1: ", default="Player_1", maxchar=10)
p_two_name = menu.add.text_input("Player_2: ", default="Player_2", maxchar=10)
menu.add.selector("Difficulty: ", [("Very easy", 0), ("Easy", 1), ("Medium", 2),
                                  ("Hard", 3), ("Very hard", 4)], onchange=change_difficulty)
menu.add.button("Play!", start)
menu.add.button("Quit.", close)


class Card:

    def __init__(self, coord_x, coord_y, width, height, border, typical_color, guess_color=None):

        self.rect = pygame.Rect(coord_x, coord_y, width, height)
        self.border = border
        self.typical_color = typical_color
        self.guess_color = guess_color
        self.selected = False

class Game:

    def __init__(self, n_1, n_2, window, diffuculty):

        self.WINDOW = window
        self.WIDTH = self.WINDOW.get_width()
        self.HEIGHT = self.WINDOW.get_height()
        self.FPS = 60
        self.LEVELS = [[16, 4], [20, 5], [28, 7], [36, 9],
                                           [40, 8]]
        self.CARDS_AMOUNT = self.LEVELS[diffuculty]
        self.PLAYER_1_NAME = n_1
        self.PLAYER_2_NAME = n_2
        self.BETWEEN_DISTANCE = 50
        self.CARD_BORDER = 1
        self.ORANGE = (252, 226, 91)
        self.WHITE = (240, 240, 240)
        self.COLORS = {(255, 0, 0):0, (255, 207, 207):0, (255, 0, 170):0,
                       (229, 5, 250):0, (98, 0, 255):0, (0, 225, 255):0,
                       (0, 255, 55):0, (204, 255, 0):0, (99, 140, 11):0,
                       (61, 53, 52):0}
        self.BLUE = (8, 16, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 9)
        self.STAT_TEXT = pygame.font.SysFont("Times New Roman", 35)
        self.END_TEXT = pygame.font.SysFont("Times New Roman", 80)
        self.CORRECT_CHOICE = pygame.mixer.Sound(os.path.join("Assets", "correct.mp3"))
        self.CORRECT_CHOICE.set_volume(0.1)
        self.WRONG_CHOICE = pygame.mixer.Sound(os.path.join("Assets", "wrong.mp3"))
        self.WRONG_CHOICE.set_volume(0.1)
        self.P1_WINS = pygame.USEREVENT + 1
        self.P2_WINS = pygame.USEREVENT + 2
        self.NO_WINS = pygame.USEREVENT + 3

        pygame.display.set_caption("Guess the cards")
        pygame.display.set_icon(pygame.image.load(os.path.join("Assets", "mega_card.png")))

        self.clock = pygame.time.Clock()
        self.run = True
        self.clickable = True
        self.end = False
        self.cards = []
        self.timer_right = Timer(2, self.on_right_guessing)
        self.timer_wrong = Timer(2, self.on_wrong_guessing)
        self.message_timer = Timer(5, self.back_to_menu)
        self.sel_cards = []
        self.create_cards()
        self.current_player = False
        self.scores = [0, 0]
        self.end_text = self.END_TEXT.render("", True, self.WHITE)

        self.main()

    def create_cards(self):

        end_x, end_y = self.WIDTH - 10, self.HEIGHT - 100
        start_x, start_y = self.WIDTH - end_x, self.HEIGHT - end_y
        amount_on_row = self.CARDS_AMOUNT[0] // self.CARDS_AMOUNT[1]
        width = (end_x - start_x - amount_on_row*self.BETWEEN_DISTANCE) // amount_on_row
        height = (end_y - start_y - self.CARDS_AMOUNT[1]*self.BETWEEN_DISTANCE) // self.CARDS_AMOUNT[1]

        for i in range(self.CARDS_AMOUNT[1]):
            for j in range(amount_on_row):
                card = Card(start_x, start_y, width, height, 1, self.WHITE)
                self.cards.append(card)
                start_x += (width + self.BETWEEN_DISTANCE)

            start_x = self.WIDTH - end_x
            start_y += (height + self.BETWEEN_DISTANCE)

        cards = [i for i in range(self.CARDS_AMOUNT[0])]
        while len(cards):
            card_1 = random.choice(cards)
            cards.remove(card_1)
            card_2 = random.choice(cards)
            cards.remove(card_2)
            color = random.choice(list(self.COLORS.keys()))
            self.cards[card_1].guess_color = color
            self.cards[card_2].guess_color = color

            self.COLORS[color] += 1
            if self.COLORS[color] == 2:
                self.COLORS.pop(color)



    def draw_window(self):
        self.WINDOW.fill(self.ORANGE)

        player_1 = self.STAT_TEXT.render(f"{self.PLAYER_1_NAME}: {self.scores[0]}", True, self.BLUE)
        player_2 = self.STAT_TEXT.render(f"{self.PLAYER_2_NAME}: {self.scores[1]}", True, self.RED)
        info_text = self.STAT_TEXT.render(f"{self.PLAYER_1_NAME} turn" if not self.current_player else f"{self.PLAYER_2_NAME} turn", True,
                                          self.BLUE if not self.current_player else self.RED)

        for card in self.cards:
            pygame.draw.rect(self.WINDOW, card.typical_color if not card.selected else card.guess_color, card.rect)

        self.WINDOW.blit(player_1, (10, self.HEIGHT - 50))
        self.WINDOW.blit(player_2, (self.WIDTH-200, self.HEIGHT-50))
        self.WINDOW.blit(info_text, (self.WIDTH//2-info_text.get_width()//2, 20))
        if self.end:
            self.WINDOW.blit(self.end_text,(self.WIDTH//2-self.end_text.get_width()//2,
                                            self.HEIGHT//2-self.end_text.get_height()//2))

        pygame.display.update()

    def main(self):

        while self.run:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.run = False
                    pygame.quit()


                if event.type == pygame.MOUSEBUTTONDOWN and self.clickable and  not self.end:
                    self.select_card(pygame.mouse.get_pos())

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.run = False

                if event.type in [self.P1_WINS, self.P2_WINS, self.NO_WINS]:
                    self.end = True
                    self.message_timer.start()

            self.draw_window()


    def back_to_menu(self):
        self.run = False


    def define_winner(self):

        remained_pairs = len(self.cards)//2
        player_1_score = self.scores[0]
        player_2_score = self.scores[1]

        if player_1_score > player_2_score + remained_pairs:
            self.end_text = self.END_TEXT.render(f"{self.PLAYER_1_NAME} WINS", True, self.BLUE)
            pygame.event.post(pygame.event.Event(self.P1_WINS))
        elif player_2_score > player_1_score + remained_pairs:
            self.end_text = self.END_TEXT.render(f"{self.PLAYER_2_NAME} WINS", True, self.RED)
            pygame.event.post(pygame.event.Event(self.P2_WINS))
        elif len(self.cards) == 0 and player_1_score == player_2_score:
            self.end_text = self.END_TEXT.render("IT'S DRAW!", True, self.GREEN)
            pygame.event.post(pygame.event.Event(self.NO_WINS))


    def add_score(self, score, change_player=True):
        self.scores[self.current_player] += score

        if change_player:
            self.current_player = not self.current_player

    def on_right_guessing(self):

        remove_on = []
        for card in range(len(self.cards)-1, -1, -1):
            if self.cards[card] in self.sel_cards:
                remove_on.append(card)

        for index in remove_on:
            self.cards.remove(self.cards[index])

        self.sel_cards = []
        self.add_score(1, False)
        self.define_winner()

        self.timer_right = Timer(2, self.on_right_guessing)
        self.clickable = True

    def on_wrong_guessing(self):
        for card in self.sel_cards:
            card.selected = False
        self.sel_cards = []

        self.add_score(0)
        self.timer_wrong = Timer(2, self.on_wrong_guessing)
        self.clickable = True

    def check_selections(self):

        self.sel_cards = [card for card in self.cards if card.selected]
        if len(self.sel_cards) != 2:
            return
        self.clickable = False
        if self.sel_cards[0].guess_color == self.sel_cards[1].guess_color:
            self.timer_right.start()
            self.CORRECT_CHOICE.play()
            return
        self.WRONG_CHOICE.play()
        self.timer_wrong.start()

    def select_card(self, mpos):

        for card in self.cards:
            if card.rect.collidepoint(mpos) and not card.selected:
                card.selected = True
                self.check_selections()


if __name__ == "__main__":

    try:
        menu.mainloop(WINDOW)
    except:
        pass