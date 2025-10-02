class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, char_type):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.direction = direction

        # Set the bullet image based on who is shooting
        if char_type == 'fire':
            self.image = bullet_img  # Fire bullet image for the player
        elif char_type == 'Golem' or char_type == 'mini1':
            self.image = bullet_img  # Earth bullet image for enemies

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
		self.rect.x += (self.direction * self.speed) + screen_scroll
		print(f"Bullet position: {self.rect.x}, {self.rect.y}")

        # Remove bullet if it goes off the screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()  # Remove the bullet if it goes off-screen

        # Check for collision with obstacles (level collision)
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()  # Remove the bullet if it hits an obstacle

        # Check if the bullet collides with the player
		if pygame.sprite.spritecollide(player, bullet_group, False):
			print("Bullet hit player!")  # Debugging collision
			if player.alive:
				player.health -= 5  # Decrease player health
				self.kill()  # Remove the bullet

		# Check if the bullet collides with an enemy
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				print("Bullet hit enemy!")
			if enemy.alive and enemy.char_type != 'mini1':
				enemy.health -= 25 
				self.kill() 
			else:
				enemy.health -= 10  
				self.kill()
