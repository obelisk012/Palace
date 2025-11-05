import pygame
import random

pygame.init()

FPS = 60

# Codes
PLAY = pygame.K_RETURN

# Burn Pile
class BurnPile():
    def __init__(self, pos: tuple = (0, 0)):
        self.cards = []
        self.rotations = []
        self.rot_cards = []
        self.pos = pos

    def draw_pile(self, screen):
        index = 0
        x, y = self.pos

        for card in self.cards:
            surface = pygame.transform.rotate(card.front_surface, random.randrange(-25, 25))
            if card not in self.rot_cards:
                self.rotations.append(surface)
                self.rot_cards.append(card)
            blit_surface= self.rotations[self.cards.index(card)]
            screen.blit(blit_surface, (x + int(index/3), y - index))
            index += 0.1

# Discard Pile
class DiscardPile():
    def __init__(self, pos: tuple = (0, 0)):
        self.cards = []
        self.rotations = []
        self.rot_cards = []
        self.pos = pos

        self.shake_active = True
        self.shake_duration = 0
        self.shake_intensity = 0

    def start_shake(self, duration_frames, intensity):
        self.shake_active = True
        self.shake_duration = duration_frames
        self.shake_intensity = intensity

    def eval(self, player_hand, event):
        for card in self.cards:
                rect = card.front_surface.get_rect(topleft=(self.pos[0], self.pos[1]))
                if rect.collidepoint(event.pos):
                    length = len(player_hand.hand)
                    tick = 0
                    for card in player_hand.hand:
                        if evaluate_hand([card], self) > 0:
                            self.start_shake(7, 12)
                            break
                        if tick == length - 1:
                            for card in self.cards:
                                card.selected = False
                                player_hand.hand.append(card)
                            self.cards = []
                            self.rotations = []
                            self.rot_cards = []
                        tick += 1

    def pickup(self, player_hand):
        for card in self.cards:
            card.selected = False
            player_hand.hand.append(card)
        self.cards = []
        self.rotations = []
        self.rot_cards = []

    def draw_pile(self, screen):
        if not self.cards:
            return

        x, y = self.pos

        offset_x, offset_y = 0, 0
        if self.shake_active and self.shake_duration > 0:
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_duration -= 1
            if self.shake_duration <= 0:
                self.shake_active = False

        index = 0
        for card in self.cards:
            if card not in self.rot_cards:
                surface = pygame.transform.rotate(card.front_surface, random.randrange(-5, 5))
                self.rotations.append(surface)
                self.rot_cards.append(card)
            blit_surface = self.rotations[self.cards.index(card)]
            screen.blit(blit_surface, (x + offset_x + int(index/3), y + offset_y - index))
            index += 0.1

# Buttons
class Button():
    def __init__(self, x: int, y: int, width: int, height: int, color: tuple = (0, 0, 0), image: str = '', button_val:int = -1):
        self.rect = pygame.Rect(x, y, width, height)
        self.image_path = ''
        self.surface = pygame.Surface((96, 32))
        self.downsurface = pygame.Surface((96, 32))
        self.down = False
        self.set_image(image, (width, height))
        self.button_val = button_val

    def draw_button(self, screen):
        if not self.down:
            screen.blit(self.surface, (self.rect.x, self.rect.y))
        else:
            screen.blit(self.downsurface, (self.rect.x, self.rect.y))

    def is_clicked(self, mouse_pos: tuple):
        return self.rect.collidepoint(mouse_pos)

    def set_image(self, image_path: str, scale: tuple = (0, 0)):
        self.image_path = image_path
        image = pygame.image.load(image_path).convert_alpha()
        self.surface.blit(image, (0, 0))   
        if scale != (0, 0):
            self.surface = pygame.transform.scale(self.surface, scale) 
            self.downsurface = pygame.transform.scale(self.surface, scale)

    def action(self):
        self.down = True
        return self.button_val

class ButtonManager():
    def __init__(self):
        self.buttons = []

    def add_button(self, button: Button):
        self.buttons.append(button)

    def draw_buttons(self, screen):
        for button in self.buttons:
            button.draw_button(screen)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Functions
def clamp(min: int, max: int, num: int):
    if num < min:
        return min
    elif num > max:
        return max
    else:
        return num
    
class PlayerHand():
    def __init__(self, min_hand_size):
        self.hand = []
        self.min_hand_size = min_hand_size
        self.shake_active = False
        self.shake_duration = 0
        self.shake_intensity = 5
        self.selshake = False

        self.selections = []

    def start_shake(self, duration_frames, intensity, toshake: int = 0):
        self.shake_active = True
        self.shake_duration = duration_frames
        self.shake_intensity = intensity
        if toshake == 0:
            self.selshake = True
        elif toshake == 1:
            self.undershake = True

    def draw_hand(self, screen):
        anchor = (475, 725)
        card_w = 144
        max_len = 810

        n = len(self.hand)
        if n == 0:
            return

        if n * card_w <= max_len:
            spacing = card_w
        else:
            spacing = (max_len - card_w) / (n - 1) if n > 1 else 0

        total_width = card_w + spacing * (n - 1)
        start_x = anchor[0] - (total_width / 2)
        y = anchor[1]

        x = start_x
        length = len(self.hand)
        tick = 0
        for card in self.hand:
            card.x, card.y = x, y

            if self.shake_active and self.shake_duration > 0:
                offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
                offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
                if card.selected:
                    card.start_shake(self.shake_duration, self.shake_intensity)
                if self.shake_duration <= 0:
                    self.shake_active = False
            
            if tick == length - 1:
                self.shake_duration -= 1
            tick += 1

            offset_x, offset_y = 0, 0
            if card.selected and card.shake_active:
                offset_x, offset_y = card.update_shake()

            card.flipped = False
            card.draw_card(screen, (x + offset_x, y + offset_y))
            x += spacing

    
    def play_cards(self, discard_pile: DiscardPile):
        for card in self.selections:
            if card in self.hand:
                self.hand.remove(card)
                discard_pile.cards.append(card)
        self.selections = []

# Card & deck classes
class Card():
    def __init__(self, val: int = 1, suit: int = 1, card_back: pygame.surface = pygame.Surface((0, 0))):
        # A = 0 - K = 12
        self.val = clamp(0, 12, val)

        if self.val == 0:
            self.val = 14

        self.strength = self.val

        # Hearts = 0, Diamonds = 1, Spades = 2, Clubs = 3
        self.suit = clamp(0, 3, suit)

        fx, fy, fwidth, fheight = (val*48), (suit*64), 48, 64
        front_rect = pygame.Rect(fx, fy, fwidth, fheight)

        self.front_surface = pygame.Surface((fwidth, fheight), pygame.SRCALPHA)
        image = pygame.image.load('cards/cards.png').convert_alpha()
        self.front_surface.blit(image, (0, 0), front_rect)

        self.front_surface = pygame.transform.scale(self.front_surface, (144, 192))

        self.back_surface = card_back
        self.flipped = False

        self.selected = False
        self.x = 0
        self.y = 0

        self.offset = 50
        self.shake_active = True
        self.shake_duration = 0
        self.shake_intensity = 0

    def start_shake(self, duration_frames, intensity):
        self.shake_active = True
        self.shake_duration = duration_frames
        self.shake_intensity = intensity

    def update_shake(self):
        """Update shake timers and return the current offset (x, y)."""
        if self.shake_active:
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_duration -= 1
            if self.shake_duration <= 0:
                self.shake_active = False
            return offset_x, offset_y
        return 0, 0

    def draw_card(self, screen, pos: tuple = (0, 0)):
        if self.selected:
            pos_list = list(pos)
            screen.blit(self.front_surface, (pos_list[0], pos_list[1] - self.offset))
            return
        if not self.flipped:
            screen.blit(self.front_surface, pos)
        else:
            screen.blit(self.back_surface, pos)

    def get_val_str(self):
        match self.val:
            case 1:
                return 'Ace'
            case 11:
                return 'Jack'
            case 12:
                return 'Queen'
            case 13:
                return 'King'
            case _:
                return str(self.val)
    
    def get_suit_str(self):
        match self.suit:
            case 0:
                return 'Hearts'
            case 1:
                return 'Diamonds'
            case 2:
                return 'Spades'
            case 3:
                return 'Clubs'
            case _:
                return 'I CODED SOMETHING WRONG'
            
    def flip(self):
        if self.flipped:
            self.flipped = False
        else:
            self.flipped = True

    def select(self, player: PlayerHand, offset: int = 50):
        if not self.selected:
            self.selected = True
            self.offset = offset
            player.selections.append(self)
            return
        self.selected = False
        if self in player.selections:
            player.selections.remove(self)
            self.offset = 0

class Deck():
    def __init__(self, max_hand_size: int = 4):
        self.cards = []
        bx, by, bwidth, bheight = 0, 256, 48, 64
        back_rect = pygame.Rect(bx, by, bwidth, bheight)

        self.back_surface = pygame.Surface((bwidth, bheight), pygame.SRCALPHA)
        image = pygame.image.load('cards/cards.png').convert_alpha()
        self.back_surface.blit(image, (0, 0), back_rect)

        self.back_surface = pygame.transform.scale(self.back_surface, (144, 192))

        for suit in range(4):
            for n in range(13):
                val = n

                self.cards.append(Card(val, suit, self.back_surface))
        
        self.current = self.cards

        self.anchor = (1100, 350)

        self.discards = []

    # Draw Functions

    def draw_deck(self, screen):
        index = 0

        x = self.anchor[0]
        y = self.anchor[1]

        for card in self.current:
            screen.blit(card.back_surface, (x+int(index/3), y-index))
            index+=0.5
            

    # Print functions
    
    def print_full_deck(self):
        for card in self.cards:
            print(f'{card.get_val_str()} of {card.get_suit_str()}')
    
    def print_current_deck(self):
        for card in self.current:
            print(f'{card.get_val_str()} of {card.get_suit_str()}')

    def print_hand(self):
        for card in self.hand:
            print(f'{card.get_val_str()} of {card.get_suit_str()}')

    def print_discards(self):
        for card in self.discards:
            print(f'{card.get_val_str()} of {card.get_suit_str()}')
    
    # Card management

    def shuffle(self):
        all_cards = self.cards
        new_cards = []

        for _ in range(len(self.cards)):
            card = random.choice(all_cards)
            all_cards.remove(card)
            new_cards.append(card)
        
        self.cards = new_cards
        self.current = self.cards
        self.discards = []
    
    def get_card(self, player: PlayerHand = PlayerHand(4), n: int = 1):
        for _ in range(n):
            card = self.current[0]

            self.current.remove(card)
            player.hand.append(card)

    def discard(self, index: int = 0):
        card = self.hand[clamp(0, len(self.hand), index)]
        self.hand.remove(card)
        self.discards.append(card) 

class UnderHand():
    def __init__(self, deck: Deck, pos: tuple = (0, 0)):
        self.cards = []
        self.pos = pos
        x, y = pos
        for i in range(3):
            card = random.choice(deck.current)
            deck.current.remove(card)
            card.position = (x + i * 150, y)
            self.cards.append(card)

    def draw_underhand(self, screen):
        for card in self.cards:
            offset_x = offset_y = 0
            if getattr(card, "shake_active", False) and card.shake_duration > 0:
                offset_x = random.randint(-card.shake_intensity, card.shake_intensity)
                offset_y = random.randint(-card.shake_intensity, card.shake_intensity)
                card.shake_duration -= 1
                if card.shake_duration <= 0:
                    card.shake_active = False

            card_x, card_y = card.position
            card.flipped = True
            card.draw_card(screen, (card_x + offset_x, card_y + offset_y))

    def start_card_shake(self, card, duration_frames, intensity):
        card.shake_active = True
        card.shake_duration = duration_frames
        card.shake_intensity = intensity

    def play_card(self, card, discard_pile: DiscardPile, player_hand: PlayerHand):
        if card in self.cards:
            match evaluate_hand([card], discard_pile):
                case 0:
                    self.cards.remove(card)
                    discard_pile.cards.append(card)
                    discard_pile.pickup(player_hand)         
                case 1:
                    self.cards.remove(card)
                    discard_pile.cards.append(card)
                case 2:
                    self.cards.remove(card)
                    discard_pile.cards.append(card)
                case 3:
                    self.cards.remove(card)
                    discard_pile.cards.append(card)
                    for card in discard_pile.cards:
                        burn_pile.cards.append(card)
                    discard_pile.cards = []
                    discard_pile.rotations = []
                    discard_pile.rot_cards = []
                    screen_start_shake(40, 25)
                case 5:
                    self.cards.remove(card)
                    discard_pile.cards.append(card)
                    strength = discard_pile.cards[-1].strength if discard_pile.cards else 8
                    card.strength = strength         

class OverHand():
    def __init__(self, deck: Deck, pos: tuple = (0, 0)):
        self.cards = []
        self.pos = pos
        x, y = pos
        for i in range(3):
            card = random.choice(deck.current)
            deck.current.remove(card)
            card.position = (x + i * 150, y)
            self.cards.append(card)

    def draw_overhand(self, screen):
        for card in self.cards:
            offset_x = offset_y = 0
            if getattr(card, "shake_active", False) and card.shake_duration > 0:
                offset_x = random.randint(-card.shake_intensity, card.shake_intensity)
                offset_y = random.randint(-card.shake_intensity, card.shake_intensity)
                card.shake_duration -= 1
                if card.shake_duration <= 0:
                    card.shake_active = False

            card_x, card_y = card.position
            card.flipped = False
            card.draw_card(screen, (card_x + offset_x, card_y + offset_y))

    def start_card_shake(self, card, duration_frames, intensity):
        card.shake_active = True
        card.shake_duration = duration_frames
        card.shake_intensity = intensity

    def play_card(self, card, discard_pile: DiscardPile, player_hand: PlayerHand):
        if card in self.cards:
            match evaluate_hand([card], discard_pile):
                case 0:
                    self.cards.remove(card)
                    discard_pile.cards.append(card)
                    discard_pile.pickup(player_hand)         
                case 1:
                    self.cards.remove(card)
                    discard_pile.cards.append(card)
                case 2:
                    self.cards.remove(card)
                    discard_pile.cards.append(card)
                case 3:
                    self.cards.remove(card)
                    discard_pile.cards.append(card)
                    for card in discard_pile.cards:
                        burn_pile.cards.append(card)
                    discard_pile.cards = []
                    discard_pile.rotations = []
                    discard_pile.rot_cards = []
                    screen_start_shake(40, 25)
                case 5:
                    self.cards.remove(card)
                    discard_pile.cards.append(card)
                    strength = discard_pile.cards[-1].strength if discard_pile.cards else 8
                    card.strength = strength   

class Player():
    def __init__(self, deck: Deck, name: str = 'Player', start: bool = True):
        self.name = name
        self.hand = PlayerHand(4)
        self.underhand = UnderHand(deck, (950, 725))
        self.overhand = OverHand(deck, (955, 710))
        self.flipped = False  
        self.is_turn = start
    
    def draw(self, screen):
        self.hand.draw_hand(screen)
        self.underhand.draw_underhand(screen)
        self.overhand.draw_overhand(screen)

    def turn(self):
        pass

def evaluate_hand(hand: list[Card], discard: DiscardPile) -> int:
    """
    0 - invalid play
    1 - normal play
    2 - play power 2 (reset and go again)
    3 - play power 10 (burn)
    4 - ????? not here
    5 - play power 8 (copy)
    """

    if not discard.cards:
        return 1

    if not hand:
        return 0

    first_val = hand[0].val
    for card in hand:
        if card.val != first_val:
            return 0

    val = first_val

    if val == 1:
        return 2 
    if val == 9:
        return 3
    if val == 7:
        return 5
    if val == 6:
        return 1

    top_val = discard.cards[-1].strength

    if top_val != 6:
        if val >= top_val:
            return 1
        else:
            return 0
    else:
        if val <= top_val:
            return 1
        else:
            return 0

# Screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
game_buffer = pygame.Surface((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Palace')

# Clock
clock = pygame.time.Clock()

# Game Variables
deck = Deck()
deck.shuffle()
player_hand = PlayerHand(4)
underhand = UnderHand(deck, (950, 725))
overhand = OverHand(deck, (955, 710))
player1 = Player(deck, 'player1', True)
flipped = False

button_manager = ButtonManager()
discard_pile = DiscardPile((600, 350))
burn_pile = BurnPile((150, 350))

mouse_down = False

shake_active = False
shake_duration = 0
shake_intensity = 5 

admin_commands = False

def screen_start_shake(duration_frames, intensity):
    global shake_active, shake_duration, shake_intensity
    shake_active = True
    shake_duration = duration_frames
    shake_intensity = intensity

# Game Loop
running = True
while running:
    game_buffer = pygame.Surface(screen.get_size())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LSHIFT] and keys[pygame.K_RSHIFT]:
                admin_commands = not admin_commands
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_RETURN:
                match evaluate_hand(player_hand.selections, discard_pile):
                    case 0:
                        player1.hand.start_shake(7, 12)
                    case 1:
                        player1.hand.play_cards(discard_pile)
                    case 2:
                        player1.hand.play_cards(discard_pile)
                    case 3:
                        player1.hand.play_cards(discard_pile)
                        for card in discard_pile.cards:
                            burn_pile.cards.append(card)
                        discard_pile.cards = []
                        discard_pile.rotations = []
                        discard_pile.rot_cards = []
                        screen_start_shake(40, 25)
                    case 5:
                        strength = discard_pile.cards[-1].strength if discard_pile.cards else 0
                        for card in player1.hand.selections:
                            card.strength = strength
                        player1.hand.play_cards(discard_pile)
                    case _:
                        pass
            # Admin commands start
            elif admin_commands:
                # Draw card
                if event.key == pygame.K_s:
                    deck.get_card(player_hand, 1)
                # Draw whole deck
                elif event.key == pygame.K_a:
                    deck.get_card(player_hand, len(deck.current))
                # Pick up discard pile
                elif event.key == pygame.K_d:
                    discard_pile.pickup(player_hand)
                elif event.key == pygame.K_f:
                    for card in discard_pile.cards:
                        burn_pile.cards.append(card)
                    discard_pile.cards = []
                    discard_pile.rotations = []
                    discard_pile.rot_cards = []
                    screen_start_shake(40, 25)
                elif event.key == pygame.K_g:
                    for card in player_hand.hand:
                        burn_pile.cards.append(card)
                    player_hand.hand = []
                    screen_start_shake(40, 25)
            # Admin commands end
        # TODO: implement player 1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in button_manager.buttons:
                if button.is_clicked(event.pos):
                    button.down = True
                    button.action()
            selected_card = False
            for card in list(reversed(player1.hand.hand)):
                if selected_card:
                    break
                if card.selected:
                    rect = card.front_surface.get_rect(topleft=(card.x, card.y - card.offset))
                else:
                    rect = card.front_surface.get_rect(topleft=(card.x, card.y))
                if rect.collidepoint(event.pos):
                    card.select(player1.hand, offset=50)
                    selected_card = True
            discard_pile.eval(player1.hand, event)
            for card in player1.underhand.cards:
                card_x, card_y = card.position
                rect = card.back_surface.get_rect(topleft=(card_x, card_y))
                if rect.collidepoint(event.pos):
                    if len(deck.cards) <= 0 and len(player1.overhand.cards) <= 0 and len(player1.hand.hand) <= 0:
                        player1.underhand.play_card(card, discard_pile, player1.hand)
                    else:
                        player1.underhand.start_card_shake(card, 7, 12)
            for card in player1.overhand.cards:
                card_x, card_y = card.position
                rect = card.front_surface.get_rect(topleft=(card_x, card_y))
                if rect.collidepoint(event.pos):
                    if len(deck.cards) <= 0 and len(player1.hand.hand) <= 0:
                        player1.overhand.play_card(card, discard_pile, player1.hand)
                    else:
                        player1.overhand.start_card_shake(card, 7, 12)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for button in button_manager.buttons:
                button.down = False

    try:
        if len(player1.hand.hand) < player1.hand.min_hand_size:
            deck.get_card(player1.hand, player1.hand.min_hand_size - len(player1.hand.hand))
    except IndexError:
        pass
    
    if len(discard_pile.cards) >= 4:
        if discard_pile.cards[-1].val == discard_pile.cards[-2].val == discard_pile.cards[-3].val == discard_pile.cards[-4].val:
            for card in discard_pile.cards:
                burn_pile.cards.append(card)
            discard_pile.cards = []
            discard_pile.rotations = []
            discard_pile.rot_cards = []
            screen_start_shake(40, 25)

    game_buffer.fill(WHITE)

    deck.draw_deck(game_buffer)

    player1.draw(game_buffer)

    discard_pile.draw_pile(game_buffer)

    burn_pile.draw_pile(game_buffer)

    button_manager.draw_buttons(game_buffer)

    offset_x, offset_y = 0, 0
    if shake_active:
        offset_x = random.randint(-shake_intensity, shake_intensity)
        offset_y = random.randint(-shake_intensity, shake_intensity)
        shake_duration -= 1
        if shake_duration <= 0:
            shake_active = False

    screen.blit(game_buffer, (offset_x, offset_y))

    pygame.display.flip()

    clock.tick(FPS)
    
pygame.quit()