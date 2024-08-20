import random

class Player:
    def __init__(self, name, serve_skill, return_skill, stamina):
        self.name = name
        self.serve_skill = serve_skill
        self.return_skill = return_skill
        self.stamina = stamina
        self.current_stamina = stamina

    def serve(self):
        serve_power = self.serve_skill * (self.current_stamina / self.stamina)
        return random.random() < (serve_power / 100)

    def hit(self):
        hit_power = self.return_skill * (self.current_stamina / self.stamina)
        return random.random() < (hit_power / 100)

    def rest(self):
        self.current_stamina = min(self.stamina, self.current_stamina + 5)

class Ball:
    def __init__(self):
        self.in_play = False

class Court:
    def __init__(self):
        self.dimensions = (23.77, 8.23)  # Length, width in meters

class Game:
    def __init__(self, server, receiver):
        self.server = server
        self.receiver = receiver
        self.score = {server: 0, receiver: 0}
        self.ball = Ball()

    def play_point(self):
        self.ball.in_play = True
        if self.server.serve():
            if not self.receiver.hit():
                return self.server
        else:
            return self.receiver

        while self.ball.in_play:
            if random.random() < 0.1:  # 10% chance of error
                self.ball.in_play = False
                return self.receiver if random.random() < 0.5 else self.server
            
            if not self.receiver.hit() or not self.server.hit():
                self.ball.in_play = False
                return self.server if self.receiver.hit() else self.receiver

        return None  # Shouldn't reach here

    def update_score(self, winner):
        score_values = {0: 0, 1: 15, 2: 30, 3: 40, 4: "Game"}
        if winner:
            self.score[winner] += 1
            if self.score[winner] >= 4 and self.score[winner] - self.score[self.get_opponent(winner)] >= 2:
                return winner
        return None

    def get_opponent(self, player):
        return self.receiver if player == self.server else self.server

    def play_game(self):
        while True:
            point_winner = self.play_point()
            game_winner = self.update_score(point_winner)
            if game_winner:
                return game_winner

class Set:
    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.score = {player1: 0, player2: 0}
        self.current_server = player1 if random.random() < 0.5 else player2

    def play_game(self):
        game = Game(self.current_server, self.get_opponent(self.current_server))
        winner = game.play_game()
        self.score[winner] += 1
        self.current_server = self.get_opponent(self.current_server)
        return self.check_set_winner()

    def get_opponent(self, player):
        return self.players[1] if player == self.players[0] else self.players[0]

    def check_set_winner(self):
        for player in self.players:
            if self.score[player] >= 6 and self.score[player] - self.score[self.get_opponent(player)] >= 2:
                return player
        return None

class Match:
    def __init__(self, player1, player2, sets_to_win=2):
        self.players = [player1, player2]
        self.score = {player1: 0, player2: 0}
        self.sets_to_win = sets_to_win
        self.current_set = None

    def play_set(self):
        self.current_set = Set(self.players[0], self.players[1])
        while True:
            set_winner = self.current_set.play_game()
            if set_winner:
                self.score[set_winner] += 1
                return set_winner

    def play_match(self):
        while max(self.score.values()) < self.sets_to_win:
            set_winner = self.play_set()
            print(f"Set won by {set_winner.name}. Current score: {self.players[0].name} {self.score[self.players[0]]} - {self.score[self.players[1]]} {self.players[1].name}")
            for player in self.players:
                player.rest()
        
        return max(self.score, key=self.score.get)

import random
import pygame
import sys
import time
import math

# [Previous Player, Ball, Court, Game, Set, and Match classes remain the same]

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
COURT_COLOR = (0, 128, 0)
LINE_COLOR = (255, 255, 255)
BALL_COLOR = (255, 255, 0)
PLAYER_COLOR = (255, 0, 0)
FONT_COLOR = (255, 255, 255)
FPS = 60

class TennisVisualization:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tennis Match Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.ball_speed = [5, 0]
        self.rally_count = 0
        self.player1_pos = [100, SCREEN_HEIGHT // 2]
        self.player2_pos = [SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2]
        self.serving = True
        self.server = 'player1'

    def draw_court(self):
        self.screen.fill(COURT_COLOR)
        pygame.draw.rect(self.screen, LINE_COLOR, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 2)
        pygame.draw.line(self.screen, LINE_COLOR, (SCREEN_WIDTH // 2, 50), (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50), 2)

    def draw_players(self):
        pygame.draw.circle(self.screen, PLAYER_COLOR, (int(self.player1_pos[0]), int(self.player1_pos[1])), 20)
        pygame.draw.circle(self.screen, PLAYER_COLOR, (int(self.player2_pos[0]), int(self.player2_pos[1])), 20)

    def draw_ball(self):
        pygame.draw.circle(self.screen, BALL_COLOR, (int(self.ball_pos[0]), int(self.ball_pos[1])), 10)

    def move_ball(self):
        if self.serving:
            if self.server == 'player1':
                self.ball_pos = [self.player1_pos[0] + 30, self.player1_pos[1]]
            else:
                self.ball_pos = [self.player2_pos[0] - 30, self.player2_pos[1]]
        else:
            self.ball_pos[0] += self.ball_speed[0]
            self.ball_pos[1] += self.ball_speed[1]

            # Apply gravity
            self.ball_speed[1] += 0.5

            # Bounce off the ground
            if self.ball_pos[1] >= SCREEN_HEIGHT - 60:
                self.ball_pos[1] = SCREEN_HEIGHT - 60
                self.ball_speed[1] = -self.ball_speed[1] * 0.8

            # Check if ball reaches a player
            if (self.ball_pos[0] <= self.player1_pos[0] + 30 and abs(self.ball_pos[1] - self.player1_pos[1]) < 50) or \
               (self.ball_pos[0] >= self.player2_pos[0] - 30 and abs(self.ball_pos[1] - self.player2_pos[1]) < 50):
                self.ball_speed[0] *= -1
                self.ball_speed[1] = random.uniform(-10, -5)
                self.rally_count += 1

    def move_players(self):
        # Simple AI: move towards the ball's y-position
        self.player1_pos[1] += (self.ball_pos[1] - self.player1_pos[1]) * 0.1
        self.player2_pos[1] += (self.ball_pos[1] - self.player2_pos[1]) * 0.1

        # Keep players within the court
        self.player1_pos[1] = max(70, min(self.player1_pos[1], SCREEN_HEIGHT - 70))
        self.player2_pos[1] = max(70, min(self.player2_pos[1], SCREEN_HEIGHT - 70))

    def draw_score(self, match, current_set, current_game):
        match_score_text = f"Match: {match.players[0].name} {match.score[match.players[0]]} - {match.score[match.players[1]]} {match.players[1].name}"
        set_score_text = f"Set: {current_set.score[match.players[0]]} - {current_set.score[match.players[1]]}"
        game_score_text = f"Game: {current_game.score[current_game.server]} - {current_game.score[current_game.receiver]}"
        rally_text = f"Rally: {self.rally_count}"
        
        match_score_surface = self.font.render(match_score_text, True, FONT_COLOR)
        set_score_surface = self.font.render(set_score_text, True, FONT_COLOR)
        game_score_surface = self.font.render(game_score_text, True, FONT_COLOR)
        rally_surface = self.font.render(rally_text, True, FONT_COLOR)
        
        self.screen.blit(match_score_surface, (10, 10))
        self.screen.blit(set_score_surface, (10, 50))
        self.screen.blit(game_score_surface, (10, 90))
        self.screen.blit(rally_surface, (10, 130))

    def update_display(self, match, current_set, current_game):
        self.draw_court()
        self.move_players()
        self.move_ball()
        self.draw_players()
        self.draw_ball()
        self.draw_score(match, current_set, current_game)
        pygame.display.flip()
        self.clock.tick(FPS)

def main():
    player1 = Player("Roger", serve_skill=90, return_skill=85, stamina=95)
    player2 = Player("Rafa", serve_skill=85, return_skill=90, stamina=98)
    
    match = Match(player1, player2)
    visualization = TennisVisualization()

    running = True
    current_set = Set(match.players[0], match.players[1])
    current_game = Game(current_set.current_server, current_set.get_opponent(current_set.current_server))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if max(match.score.values()) < match.sets_to_win:
            visualization.update_display(match, current_set, current_game)
            
            if visualization.serving:
                visualization.serving = False
                visualization.ball_speed = [10 if visualization.server == 'player1' else -10, -10]

            # End point if ball goes out of bounds
            if visualization.ball_pos[0] < 50 or visualization.ball_pos[0] > SCREEN_WIDTH - 50:
                point_winner = current_game.play_point()
                game_winner = current_game.update_score(point_winner)
                
                if game_winner:
                    current_set.score[game_winner] += 1
                    current_set.current_server = current_set.get_opponent(current_set.current_server)
                    current_game = Game(current_set.current_server, current_set.get_opponent(current_set.current_server))
                    
                    set_winner = current_set.check_set_winner()
                    if set_winner:
                        match.score[set_winner] += 1
                        print(f"Set won by {set_winner.name}. Current score: {match.players[0].name} {match.score[match.players[0]]} - {match.score[match.players[1]]} {match.players[1].name}")
                        for player in match.players:
                            player.rest()
                        current_set = Set(match.players[0], match.players[1])
                
                # Reset for next serve
                visualization.serving = True
                visualization.server = 'player1' if current_game.server == match.players[0] else 'player2'
                visualization.rally_count = 0

        else:
            winner = max(match.score, key=match.score.get)
            print(f"\nMatch winner: {winner.name}")
            print(f"Final score: {player1.name} {match.score[player1]} - {match.score[player2]} {player2.name}")
            
            # Display the final result
            final_text = f"Winner: {winner.name} ({match.score[player1]} - {match.score[player2]})"
            final_surface = visualization.font.render(final_text, True, FONT_COLOR)
            visualization.screen.blit(final_surface, (SCREEN_WIDTH // 2 - final_surface.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            
            # Wait for 5 seconds or until the user closes the window
            start_time = time.time()
            while time.time() - start_time < 5 and running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

        time.sleep(0.01)  # Slow down the simulation

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()