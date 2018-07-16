import sys
from time import sleep

import pygame

from bullet import Bullet
from alien import Alien

def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """响应按键"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()
        
def check_keyup_events(event, ship):
    """响应松开."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens,
        bullets):
    """响应按键和鼠标事件."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button,
                ship, aliens, bullets, mouse_x, mouse_y)
            
def check_play_button(ai_settings, screen, stats, sb, play_button, ship,
        aliens, bullets, mouse_x, mouse_y):
    """单击play开始新游戏"""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        # 重置游戏设置.
        ai_settings.initialize_dynamic_settings()
        
        # 隐藏鼠标光标
        pygame.mouse.set_visible(False)
        
        # 重置游戏统计数据.
        stats.reset_stats()
        stats.game_active = True
        
        # 重置计分板图片.
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()
        
        # 清空外星人和子弹.
        aliens.empty()
        bullets.empty()
        
        # 创建一群新的外星人，并且让飞船居中.
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

def fire_bullet(ai_settings, screen, ship, bullets):
    """如果没有子弹限制，就发射一个子弹"""
    # 创建新子弹，并将其加入编组bullets.
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)

def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets,
        play_button):
    """更新屏幕上的图像，并且切换到新屏幕"""
    # 每次循环都重置屏幕.
    screen.fill(ai_settings.bg_color)
    
    # 让最近绘制的屏幕可见.
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)
    
    # 显示得分.
    sb.show_score()
    
    # 如果游戏处于非活跃状态，就绘制play按钮.
    if not stats.game_active:
        play_button.draw_button()

    # 如果游戏处于非活跃状态，就绘制play按钮.
    pygame.display.flip()
    
def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """更新子弹位置，清除旧子弹 ."""
    # 更新子弹位置
    bullets.update()

    # 清除消失的旧子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
            
    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship,
        aliens, bullets)
        
def check_high_score(stats, sb):
    """检查是否有新的高分数"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
            
def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship,
        aliens, bullets):
    """响应子弹和外星人的碰撞"""
    # 删除发生碰撞的的子弹和外星人.
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)
    
    if len(aliens) == 0:
        #删除所有的子弹，并创建一个新的外星人群.
        bullets.empty()
        ai_settings.increase_speed()
        
        # 上升一级.
        stats.level += 1
        sb.prep_level()
        
        create_fleet(ai_settings, screen, ship, aliens)
    
def check_fleet_edges(ai_settings, aliens):
    """有外星人达到边缘时采取相应的措施."""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break
        
def change_fleet_direction(ai_settings, aliens):
    """将整群外星人下移，并改变他们的方向"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1
    
def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """响应被外星人撞到的飞船."""
    if stats.ships_left > 0:
        # Decrement ships_left.
        stats.ships_left -= 1
        
        # 更新计分板
        sb.prep_ships()
        
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)
    
    # 清空外星人和子弹的名单.
    aliens.empty()
    bullets.empty()
    
    # 创建一群新的外星人，并将飞船放到屏幕底部中央
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()
    
    # 暂停
    sleep(0.5)
    
def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens,
        bullets):
    """检查是否有外星人达到屏幕底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # 像飞船被撞到一样处理
            ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
            break
            
def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """
    检查是否有外星人位于屏幕边缘，并更新整群外星人的位置
    """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()
    
    # 检测外星人和飞船之间的碰撞.
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)

    # 检查是否有外星人达到屏幕底端
    check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets)
            
def get_number_aliens_x(ai_settings, alien_width):
    """确定排成一行的外星人的数量."""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x
    
def get_number_rows(ai_settings, ship_height, alien_height):
    """确定适合屏幕的外星人行数."""
    available_space_y = (ai_settings.screen_height -
                            (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows
    
def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """创造一个外星人，并把它放在一行"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

def create_fleet(ai_settings, screen, ship, aliens):
    """创造一个完整的外星人舰队"""
    # 创建一个外星人，并计算一行可以容纳多少个外星人.
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height,
        alien.rect.height)
    
    # 创建外星人群
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number,
                row_number)
