import sys
from time import sleep
import pygame
from bullet import Bullet
from ship import Ship
from alien import Alien
from pygame.sprite import Sprite
from scoreboard import Scoreboard

def check_events(ship,ai_settings,screen,bullets,play_button,stats,aliens,sb):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen,ship,bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event,ship)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y = pygame.mouse.get_pos()
            check_play_button(stats,play_button,mouse_x,mouse_y,aliens,ship,bullets,ai_settings,screen,sb)

def check_keydown_events(event,ai_settings,screen,ship,bullets):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        if len(bullets) < ai_settings.bullets_allowed:
            new_bullet = Bullet(ai_settings,screen,ship)
            bullets.add(new_bullet)
    elif event.key == pygame.K_q:
        sys.exit()

def check_keyup_events(event,ship):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def update_screen(ai_settings,screen,ship,bullets,alien,aliens,play_button,stats,sb):
    screen.fill(ai_settings.bg_color)
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)
    sb.show_score()
    #Draw the play button if the game is inactive.
    if not stats.game_active:
        play_button.draw_button()

    # alien.blitme()
    pygame.display.flip()

def update_ship(ship):
    ship.update()

def update_bullets(ai_settings,screen,ship,aliens, bullets,sb,stats):
    bullets.update()

    check_bullet_alien_collisions(ai_settings,screen,ship,aliens,bullets,sb,stats)
    
def check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets,sb,stats):
    collisions = pygame.sprite.groupcollide(bullets,aliens,True,True)

    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points
            sb.prep_score()
        check_high_score(stats, sb)

    if len(aliens) == 0:
        #Destroy the existing bullets, speed up game, and create new fleet.
        bullets.empty()
        ai_settings.increase_speed()

        #Increase the level when fleet is destroyed 
        stats.level += 1
        sb.prep_level()
        create_fleet(ai_settings,screen,ship,aliens)

def update_aliens(aliens,ship, ai_settings,stats,screen,bullets):
    """ Chaeck if the fleet is at an edge, and then update the postions of all aliens in the fleet."""
    check_fleet_edges(ai_settings,aliens)
    aliens.update()

    #Look for alien-ship collisions.
    if pygame.sprite.spritecollideany(ship,aliens):
        ship_hit(ai_settings,stats,screen,ship,aliens,bullets)

    #Look for aliens hitting the bottom of the screen.
        check_aliens_bottom(ai_settings,stats, screen, ship, aliens, bullets)


def get_number_aliens_x(ai_settings,alien_width):
    available_space_x = ai_settings.screen_width - 2*alien_width
    number_aliens_x = int(available_space_x/(2*alien_width))
    return number_aliens_x

def get_number_row(ai_settings,alien_height,ship_height):
    available_space_y =ai_settings.screen_height -( 3* alien_height) - ship_height
    number_row = int(available_space_y/(2*alien_height))
    return number_row


def create_fleet(ai_settings,screen,ship,aliens):
    """Create a full fleet of aliens """
    # Create an alien and find the number of aliens in a row
    # Spacing between each alien is ewual to one alien width

    alien = Alien(ai_settings,screen)
    ship = Ship(screen,ai_settings)
    alien_width = alien.rect.width
    alien_height = alien.rect.height
    ship_height = ship.rect.height
    number_aliens_x =get_number_aliens_x(ai_settings,alien_width)
    number_row = get_number_row(ai_settings,alien_height,ship_height)
    # Create the first row of aliens 
    for row_number in range(number_row):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings,screen,aliens,alien_number,row_number)

def create_alien(ai_settings,screen,aliens,alien_number,row_number):
    alien = Alien(ai_settings,screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 *alien_width*alien_number
    alien.rect.y = alien.rect.height + 2*alien.rect.height *row_number
    alien.rect.x = alien.x
    aliens.add(alien)


def check_fleet_edges(ai_settings,aliens):
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            break

def change_fleet_direction(ai_settings,aliens):
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def ship_hit(ai_settings,stats,screen,ship,aliens,bullets):
    """ Respond to ship being hit by alien."""
    if stats.ships_left > 0: 
        #Decrement ships_left.
        stats.ships_left -= 1

        #Empty the list of aliens and bullets.
        aliens.empty()          
        bullets.empty()

        # Create a new fleet and center the ship.
        create_fleet(ai_settings,screen,ship,aliens)
        ship.center_ship()

        #pause 
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

def check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets):
    """ Check if any aliens have reached the bottom of the screen."""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            #Ttreat this the same as if the ship got hit
            ship_hit(ai_settings,stats,screen,ship,aliens,bullets)
            break

def check_play_button(stats, play_button,mouse_x,mouse_y,aliens,ship,bullets,ai_settings,screen,sb):
    """Start a new game when the player clicks Play."""
    button_clicked = play_button.rect.collidepoint(mouse_x,mouse_y)
    if button_clicked and not stats.game_active:
        #Hide the mouse cursor 
        pygame.mouse.set_visible(False)
        ai_settings.initialize_dynamic_settings()
        stats.reset_stats()
        stats.game_active = True

    #Reset the scoreboard images.
    sb.prep_score()
    sb.prep_high_score()
    sb.prep_level()

    #empty the list of aliens and bullets
    aliens.empty()
    bullets.empty()
    #Creat a new fleet and center the ship
    create_fleet(ai_settings,screen,ship,aliens)   
    ship.center_ship()
    
def check_high_score(stats, sb):
    """Check to see if there's a new high score."""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
