import pygame
from pygame.sprite import Sprite

class Ship(Sprite):

    def __init__(self, ai_settings, screen):
        """初始化飞船，并设置他的起始位置."""
        super(Ship, self).__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # 加载飞船图片，并获取飞船rect.
        self.image = pygame.image.load('images/sp.png')
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # 在屏幕底部中心开始每一个新飞船.
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom
        
        # 以浮点数存储飞船中心数据.
        self.center = float(self.rect.centerx)
        
        # 移动标志.
        self.moving_right = False
        self.moving_left = False
        
    def center_ship(self):
        """让飞船在屏幕居上."""
        self.center = self.screen_rect.centerx
        
    def update(self):
        """根据飞船移动更新飞船位置"""
        # 更新飞船中心值，而不是矩形.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.center += self.ai_settings.ship_speed_factor
        if self.moving_left and self.rect.left > 0:
            self.center -= self.ai_settings.ship_speed_factor
            
        # 根据self.center更新rect对象.
        self.rect.centerx = self.center

    def blitme(self):
        """绘制飞船当前位置."""
        self.screen.blit(self.image, self.rect)
