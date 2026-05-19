# -*- coding: utf-8 -*-
"""
Created on Sat May 16 20:00:21 2026

@author: panaj
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from plyer import tts
import random

zero_score = ["Go home you're drunk", "Be careful you will kill someone", "You need glasses, man", "Stop playing, go home"]
one_score = ["That was bad", "At least it's not zero", "You suck"]
sexton_score = ["Fucking A bro", "You're amazing", "Excellent shot", "Can you teach me how to do it?", "I want your autograph"]

class Player:
def __init__(self, name, country):
self.name = name
self.country = country
self.score = 301
self.finished = False
self.turn_reached_zero = -1

class DartsGameApp(App):
def build(self):
self.players = []
self.current_player_index = 0
self.current_throw = 0
self.current_turn_score = 0
self.current_throws = []
self.round_number = 1
self.phase = 'setup_players_number'
self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
self.info_label = Label(text="Enter number of players:", font_size='20sp')
self.input_box = TextInput(hint_text='Number', multiline=False, input_filter='int', font_size='20sp')
self.submit_button = Button(text='Submit', on_press=self.handle_input, font_size='20sp')
self.status_label = Label(text='', font_size='18sp')

self.layout.add_widget(self.info_label)
self.layout.add_widget(self.input_box)
self.layout.add_widget(self.submit_button)
self.layout.add_widget(self.status_label)

self.temp_players_count = 0
self.temp_player_data = []
self.temp_input_step = 'name'

return self.layout

def speak(self, message):
tts.speak(message)
self.status_label.text = message

def handle_input(self, instance):
text = self.input_box.text.strip()
if self.phase == 'setup_players_number':
if text.isdigit() and int(text) > 0:
self.temp_players_count = int(text)
self.phase = 'setup_names_countries'
self.temp_input_step = 'name'
self.info_label.text = f"Enter name for player 1:"
self.input_box.text = ''
self.input_box.input_filter = None
else:
self.speak("Enter a valid number")
elif self.phase == 'setup_names_countries':
if self.temp_input_step == 'name':
if text and not text.isdigit():
self.temp_player_data.append({'name': text})
self.temp_input_step = 'country'
self.info_label.text = f"Enter country for player {len(self.temp_player_data)}:"
self.input_box.text = ''
else:
self.speak("Enter a valid player name (letters only)")
elif self.temp_input_step == 'country':
if text and not text.isdigit():
self.temp_player_data[-1]['country'] = text
if len(self.temp_player_data) == self.temp_players_count:
self.players = [Player(d['name'], d['country']) for d in self.temp_player_data]
self.phase = 'play'
self.update_status()
self.input_box.text = ''
else:
self.temp_input_step = 'name'
self.info_label.text = f"Enter name for player {len(self.temp_player_data)+1}:"
self.input_box.text = ''
else:
self.speak("Enter a valid country name (letters only)")
elif self.phase == 'play':
self.process_throw(text)
self.input_box.text = ''

def process_throw(self, text):
try:
score = int(text)
except ValueError:
score = 0

player = self.players[self.current_player_index]

if score == 0:
self.speak(random.choice(zero_score))
elif score == 1:
self.speak(random.choice(one_score))
elif score == 2:
self.speak("You need to lay off the beers, bro")
elif score == 50:
self.speak("Bullseye")
elif score == 60:
self.speak(random.choice(sexton_score))
elif score == 20:
self.speak(f"{player.name} from {player.country}, your country is proud of you")

self.current_throws.append(score)

if sorted(self.current_throws) == [1, 5, 20]:
self.speak("The Holy Trinity!")

if player.score - (self.current_turn_score + score) < 0:
self.speak(f"Bust! {player.name} still needs {player.score} points")
self.next_player()
else:
self.current_turn_score += score
self.current_throw += 1

if player.score - self.current_turn_score == 0:
player.finished = True
player.turn_reached_zero = self.round_number

# Speak remaining score only if under 60
remaining = player.score - self.current_turn_score
if 0 < remaining < 60:
self.speak(f"{player.name}, you have {remaining} points left")

if self.current_throw == 3 or player.finished:
if not player.finished:
player.score -= self.current_turn_score
self.next_player()

self.update_status()

def next_player(self):
self.current_throw = 0
self.current_turn_score = 0
self.current_throws = []

start_index = self.current_player_index
while True:
self.current_player_index = (self.current_player_index + 1) % len(self.players)
if self.current_player_index == 0:
self.round_number += 1

if not self.players[self.current_player_index].finished:
break
if self.current_player_index == start_index:
break # everyone finished

self.check_game_over()

def check_game_over(self):
if all(p.finished or p.score == 0 for p in self.players):
winners = [p for p in self.players if p.turn_reached_zero == self.round_number - 1]
if not winners:
winners = [p for p in self.players if p.score == 0]
winner_names = ", ".join([f"{p.name} ({p.country})" for p in winners])
self.speak(f"Game over! Winner(s): {winner_names}")
self.phase = 'done'
self.info_label.text = f"Game over! Winner(s): {winner_names}"
self.input_box.disabled = True
self.submit_button.disabled = True

def update_status(self):
if self.phase == 'done':
return
player = self.players[self.current_player_index]
remaining = player.score - self.current_turn_score
self.info_label.text = (
f"Round {self.round_number} - {player.name} from {player.country}\\n"
f"Throw {self.current_throw + 1} of 3\\n"
f"Score: {player.score} → {remaining}\\nEnter score for throw:"
)

if __name__ == '__main__':
DartsGameApp().run()