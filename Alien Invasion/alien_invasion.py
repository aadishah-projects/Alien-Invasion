import pygame
from pygame.sprite import Group
from settings import Settings
from ship import Ship
import game_functions as gf
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from scoreboard import Scoreboard 
from button import Button


def run_game():
    # initialize pygame
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")
    
    # Make the Play button.
    play_button = Button(ai_settings,screen,"Play")
    stats = GameStats(ai_settings)
    sb = Scoreboard(ai_settings,screen,stats)
    ship = Ship(screen, ai_settings)
    alien = Alien(ai_settings, screen)
    bullets = Group()
    aliens = Group()
    gf.create_fleet(ai_settings, screen,ship, aliens)

    while True:
        gf.check_events(ship, ai_settings, screen, bullets,play_button,stats,aliens,sb)

        if stats.game_active:
            gf.update_ship(ship)
            gf.update_bullets(ai_settings,screen,ship,aliens,bullets,sb,stats)

            for bullet in bullets.copy():
                if bullet.rect.bottom <= 0:
                    bullets.remove(bullet)
        
            gf.update_aliens(aliens,ship, ai_settings,stats,screen,bullets)
        # aliens.update()
        # gf.check_fleet_edges(aliens,ai_settings)
        gf.update_screen(ai_settings, screen, ship, bullets, alien, aliens,play_button,stats,sb)


run_game()
