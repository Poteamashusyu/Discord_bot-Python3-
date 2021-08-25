import discord

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock



version = '0.1.0'
token = 'ODQzNDQ2MjAxMzc4Mjc1MzU4.YKD-fA.96EfKpJvwqTHeoDgq-k0uhTYCNA'

Power = 'OFF'


def button_on(self):
    print('Pressed!')
    global Power
    Power = 'ON'


class MainApp(App):
    def build_config(self, config):
        config.setdefaults('section1', {
            'key1': 'value1',
            'key2': '42'
        })

    def build(self):
        global power_btn
        config = self.config
        power_btn = Button(text=f'Power {Power}', font_size=18)
        power_btn.bind(
            on_press = lambda power_btn: button_on(self),
            on_release = lambda power_btn: print('Released!'),
        )
        Label(text='key1 is %s and key2 is %d' % (
            config.get('section1', 'key1'),
            config.getint('section1', 'key2')))
        Clock.schedule_interval(MainApp().update, 1.0 / 60.0)
        return power_btn

    def update(self, dt):
        global power_btn
        power_btn = Button(text=f'Power {Power}', font_size=18)
        return power_btn


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Start HacGame_onDiscord(Python) v{version}')
        
    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

        if(message.content == '.cd say'):
            await message.channel.send(input())

client = MyClient()

if __name__ == '__main__':
    MainApp().run()

# client.run(token)