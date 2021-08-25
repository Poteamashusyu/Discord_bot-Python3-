# -*- coding: utf-8 -*-

import os
import os.path as Path
import logging
import time 
import datetime
import copy
import math
from decimal import Decimal
import random
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import tkinter as tk

import discord
from discord.ext import commands, tasks



class Color:
    BLACK     = '\033[30m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    YELLOW    = '\033[33m'
    BLUE      = '\033[34m'
    PURPLE    = '\033[35m'
    CYAN      = '\033[36m'
    WHITE     = '\033[37m'
    END       = '\033[0m'
    BOLD      = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE   = '\033[07m'

os.chdir(os.path.dirname(__file__))
config = json.load(open("config.json", "r", encoding="utf-8"))
VERSION = config["config"]["version"]
PREFIX = config["config"]["prefix"]
TOKEN = config["SECRET"]["token"]

Owner = config["authorizer"]["owner"]

TPE = ThreadPoolExecutor(max_workers=3, thread_name_prefix='#_pcd')

client = commands.Bot(command_prefix=PREFIX)



db = {
      'messages': []
}

# functions

async def timer():
    pass
# end

def _discord_():
    othello = {
               'description': {
                               'how2put': "「`<アルファベット>` `<数字>`」とチャットし石を置いてください。"
               },
               'CantPut': 0,
               'count': [[0, 0, 0, 0], [0, 0, 0, 0]],
               'Embed_info': None,
               'format': {0: ":green_square:", 'B': ":black_circle:", 'W': ":white_circle:", 'R': ":red_circle:", 'C': ":blue_circle:", 'P': ":yellow_square:"}, # 0: 空き位置, B: 黒石, W: 白石, R: 赤石, C: 青石(水色石), P:can_Place(置ける位置)
               'Game_board': [],
               'Init_state': None,
               'mode': "stand-by",
               'players': [],
               'stones': ('B', 'W', 'R', 'C'),
               'turn': 0,
               'turn_count': 0,
               'Use_channel': None
               }
    with open('./data/othello/config.json', 'r', encoding='utf-8') as f:
        othello['Init_state'] = json.load(f)['init_state']

    class _othello_body_: # othello関数クラス
        # def __init__(self):
        #     pass
        def _othello_init_(self):
            othello['CantPut'] = 0
            othello['count'] = [[0, 0, 0, 0], [0, 0, 0, 0]]
            othello['Embed_info'] = None
            othello['Game_board'] = []
            othello['players'] = []
            othello['mode'] = "stand-by"
            othello['turn'] = 0
            othello['turn_count'] = 0
            othello['Use_channel'] = None
            print(Color.CYAN + f'---オセロの状態を初期化しました---' + Color.END)

        async def start(self, message):
            othello['Game_board'] = copy.deepcopy(othello['Init_state']['two_players']) if len(othello['players']) == 2 else copy.deepcopy(othello['Init_state']['three_players']) if len(othello['players']) == 3 else copy.deepcopy(othello['Init_state']['four_players'])
            othello['Use_channel'] = message.channel
            othello['turn_count'] = 1

            text = self.print()
            player = await discord.Client.fetch_user(client, othello["players"][othello["turn"]])
            othello['Embed_info'] = await message.channel.send(None,
                embed=discord.Embed(
                    color=0x12990b,
                    title=':arrow_forward::black_circle:オセロ:white_circle::arrow_forward:',
                    description=f':{othello["format"][othello["stones"][othello["turn"]]]}:**{player}** の番`{othello["turn_count"]}巡目{othello["turn"]+1}人目`\n' + text + othello['description']['how2put']
                )
            )
        
        def print(self, mode=None):
            text = ''
            number = (':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:')
            cp_list = self.place_check(othello['stones'][othello['turn']], mode='draw')
            for n, cl in zip(number, cp_list):
                text += n + str().join(map(str, cl)) + '\n'
            if mode == 'only_alphabet':
                return text
            else:
                for k, v in othello['format'].items():
                    text = text.replace(str(k), v)
            dif = self.stonecount()
            counttext = ''
            if 64 - sum(othello['count'][1]) > 10:
                for i, s in enumerate(othello['stones']):
                    counttext += f'{othello["format"][s]}: {othello["count"][1][i]}枚({dif[i]:+}), '
            text = counttext + '\n:negative_squared_cross_mark::regional_indicator_a::regional_indicator_b::regional_indicator_c::regional_indicator_d::regional_indicator_e::regional_indicator_f::regional_indicator_g::regional_indicator_h:\n' + text
            return text

        def next_turn(self):
            if othello['turn'] < len(othello['players'])-1:
                othello['turn'] += 1
            else:
                othello['turn'] = 0
                othello['turn_count'] += 1

        def place_check(self, stone, *, mode): # (stone: 検索する石, mode= 'coordinate': 置ける位置の座標を返すモード | 'draw': 盤面配列に置ける位置をハイライトした盤面配列を返すモード)
            can_place = []
            cp_list = [[] for _ in range(8)]
            for y in range(8):
                for x in range(8):
                    pos = [y, x]

                    if othello['Game_board'][pos[0]][pos[1]]:
                        cp_list[pos[0]].append(othello["Game_board"][pos[0]][pos[1]])
                        continue

                    none_flag = True # 周り八方向に石がないフラグ
                    for i in ((-1,-1), (-1,0), (-1,+1), (0,-1), (0,+1), (+1,-1), (+1,0), (+1,+1)): # 検索順: 左上、上、右上、左、右、左下、下、右下
                        search = pos[:]
                        temp_targ = []
                        break_flag = False # 置ける事が確認され次第処理を省くフラグ(計算量抑制)
                        while True:
                            search[0], search[1] = search[0]+i[0], search[1]+i[1]
                            if not 0 <= search[0] <= 7 or not 0 <= search[1] <= 7 or othello['Game_board'][search[0]][search[1]] == 0: # 挟み込み失敗時
                                break
                            elif othello['Game_board'][search[0]][search[1]] == stone: # 検索場所が自分の石である時
                                if len(temp_targ) >= 1: # 挟める石がある場合
                                    can_place.append(pos)
                                    break_flag = True
                                    none_flag = False
                                    cp_list[pos[0]].append('P')
                                else: # 挟める石がない場合
                                    pass
                                    # cp_list[pos[0]].append(0)
                                break
                            else: # それ以外(検索場所が相手の石である時)
                                temp_targ.append([search[0], search[1]])
                                # continue
                        if break_flag == True: break
                    if none_flag == True: cp_list[pos[0]].append(0)
            return can_place if mode == 'coordinate' else cp_list if mode == 'draw' else 'Error'
        
        async def put(self, message, posX, posY, stone):
            pos = [0, 0]
            try:
                pos[0] = int(posX, base=18)-9
                pos[1] = int(posY)
            except:
                text = self.print()
                player = await discord.Client.fetch_user(client, othello["players"][othello["turn"]])
                await othello['Embed_info'].edit(
                    embed=discord.Embed(
                        color=0x12990b,
                        title=':no_entry_sign::black_circle:オセロ:white_circle::no_entry_sign:',
                        description=f':{othello["format"][othello["stones"][othello["turn"]]]}:**{player}** の番`{othello["turn_count"]}巡目{othello["turn"]+1}人目`\n' + text + ':information_source:**※正しく座標を入力して石を置いてください。**\n' + othello['description']['how2put']
                    )
                )
                return
            pos = [pos[1]-1, pos[0]-1] # 配列で管理する都合でx, y座標を逆転させ、互いに-1しています。
            target = []

            if not 0 <= pos[0] <= 7 or not 0 <= pos[1] <= 7: # ボード範囲外設置エラー返信
                text = self.print()
                player = await discord.Client.fetch_user(client, othello["players"][othello["turn"]])
                await othello['Embed_info'].edit(
                    embed=discord.Embed(
                        color=0x12990b,
                        title=':no_entry_sign::black_circle:オセロ:white_circle::no_entry_sign:',
                        description=f':{othello["format"][othello["stones"][othello["turn"]]]}:**{player}** の番`{othello["turn_count"]}巡目{othello["turn"]+1}人目`\n' + text + ':information_source:**※ボードの外には置けません。置ける位置(黄色マス)に石を置いてください。**\n' + othello['description']['how2put']
                    )
                )
                return

            if othello['Game_board'][pos[0]][pos[1]] != 0: # すでに石が置いてあるところに置こうとした時のエラー返信
                text = self.print()
                player = await discord.Client.fetch_user(client, othello["players"][othello["turn"]])
                await othello['Embed_info'].edit(
                    embed=discord.Embed(
                        color=0x12990b,
                        title=':no_entry_sign::black_circle:オセロ:white_circle::no_entry_sign:',
                        description=f':{othello["format"][othello["stones"][othello["turn"]]]}:**{player}** の番`{othello["turn_count"]}巡目{othello["turn"]+1}人目`\n' + text + ':information_source:**※置ける位置(黄色マス)に石を置いてください。**\n' + othello['description']['how2put']
                    )
                )
                return

            for i in ((-1,-1), (-1,0), (-1,+1), (0,-1), (0,+1), (+1,-1), (+1,0), (+1,+1)): # 検索順: 左上、上、右上、左、右、左下、下、右下
                search = pos[:]
                temp_targ = []
                while True:
                    search[0], search[1] = search[0]+i[0], search[1]+i[1]
                    if not 0 <= search[0] <= 7 or not 0 <= search[1] <= 7 or othello['Game_board'][search[0]][search[1]] == 0: # 挟み込み失敗時
                        break
                    elif othello['Game_board'][search[0]][search[1]] == stone: # 検索場所が自分の石である時
                        for j in temp_targ:
                            target.append(j)
                        break
                    else: # それ以外(検索場所が相手の石である時)
                        temp_targ.append([search[0], search[1]])
                        # continue

            if len(target) > 0: # 置ける場所であるかの最終的な判定
                othello['Game_board'][pos[0]][pos[1]] = stone
            else:
                text = self.print()
                player = await discord.Client.fetch_user(client, othello["players"][othello["turn"]])
                await othello['Embed_info'].edit(
                    embed=discord.Embed(
                        color=0x12990b,
                        title=':no_entry_sign::black_circle:オセロ:white_circle::no_entry_sign:',
                        description=f':{othello["format"][othello["stones"][othello["turn"]]]}:**{player}** の番`{othello["turn_count"]}巡目{othello["turn"]+1}人目`\n' + text + f':information_source:**※置ける位置(黄色マス)に石を置いてください。**\n' + othello['description']['how2put']
                    )
                )
                return 'Failed'

            for i in target:
                othello['Game_board'][i[0]][i[1]] = stone
            
            await self.game_judge(posX, posY)

        async def game_judge(self, posX, posY):
            self.next_turn()
            can_place = self.place_check(othello['stones'][othello['turn']], mode='coordinate')
            text = self.print()
            player = await discord.Client.fetch_user(client, othello["players"][othello["turn"]])
            if len(can_place) >= 1: # 置ける位置がある場合
                othello['CantPut'] = 0
                await othello['Embed_info'].edit(
                    embed=discord.Embed(
                        color=0x12990b,
                        title=':arrow_forward::black_circle:オセロ:white_circle::arrow_forward:',
                        description=f':{othello["format"][othello["stones"][othello["turn"]]]}:**{player}** の番`{othello["turn_count"]}巡目{othello["turn"]+1}人目`\n' + text + f':ballot_box_with_check:`({posX}, {posY})`に石が置かれました。\n' + othello['description']['how2put']
                    )
                )
            
            elif othello['CantPut'] >= len(othello['players'])-1: # 誰も石を置けない場合
                await othello['Embed_info'].edit(
                    embed=discord.Embed(
                        color=0x12990b,
                        title=':asterisk::black_circle:オセロ:white_circle::asterisk:',
                        description=f':{othello["format"][othello["stones"][othello["turn"]]]}:**{player}** の番`{othello["turn_count"]}巡目{othello["turn"]+1}人目`\n' + text + ':information_source:**誰も石を置けなくなりました。**\n' + 'ゲームを終了し、結果を表示します！'
                    )
                )
                Board_text = self.print(mode='only_alphabet')
                stone_count = []
                result = ''
                for i in range(len(othello['players'])):
                    stone_count.append(Board_text.count(othello['stones'][i]))
                    player = await discord.Client.fetch_user(client, othello["players"][i])
                    result += f':{othello["format"][othello["stones"][i]]}: {player} ({stone_count[i]}枚)\n'
                first_place = stone_count.index(max(stone_count))
                player = await discord.Client.fetch_user(client, othello["players"][first_place])
                await asyncio.sleep(5)
                await othello['Embed_info'].edit(
                    embed=discord.Embed(
                        color=0x12990b,
                        title=':regional_indicator_g::black_circle:オセロ:white_circle::regional_indicator_g:',
                        description=f':crown:**勝者:{othello["format"][othello["stones"][first_place]]}:{player}**\n' + text + f'`({othello["turn_count"]-1}巡目で終了)`\n<リザルト>\n' + result + '---お疲れ様でした。オセロ初期化を行います。---'
                    )
                )
                self._othello_init_()

            else: # 石を置けない人が出た場合
                await othello['Embed_info'].edit(
                    embed=discord.Embed(
                        color=0x12990b,
                        title=':x::black_circle:オセロ:white_circle::x:',
                        description=f':{othello["format"][othello["stones"][othello["turn"]]]}:**{player}** の番`{othello["turn_count"]}巡目{othello["turn"]+1}人目`\n' + text + f':ballot_box_with_check:`({posX}, {posY})`に石が置かれました。\n' + ':x:**置ける場所がありません！出番がスキップされます...**'
                    )
                )
                othello['CantPut'] += 1
                await asyncio.sleep(3)
                await self.game_judge(posX, posY)

        def stonecount(self):
            othello['count'][0] = othello['count'][1][:]
            othello['count'][1] = [0, 0, 0, 0]
            for y in othello['Game_board']:
                for x in y:
                    for i in range(4):
                        if x == othello['stones'][i]: othello['count'][1][i] += 1
            dif = [0, 0, 0, 0]
            for i in range(4): dif[i] = othello['count'][1][i] - othello['count'][0][i]
            return dif


    class _tycoon_: # tycoon関数クラス
        async def load(self, guild_id, *, message=None):
            tycoon_address = f'./db/tycoon/{guild_id}.json'
            tycoon_file = None # jsonファイル用変数
            tycoon_info = None # チャンネルとメッセージのアクセス保持用
            try:
                with open(tycoon_address, mode='r', encoding='utf-8') as f:
                    tycoon_file = json.load(f)
            except: pass

            if tycoon_file:
                tycoon_info = { 'Tchannel': discord.Client.get_channel(client, tycoon_file['channel_id']) }
                tycoon_info['Tmessage'] = await discord.abc.Messageable.fetch_message(tycoon_info['Tchannel'], tycoon_file['embed_id'])

            return tycoon_file, tycoon_info

        async def print(self, tycoon_file, tycoon_info, *, message=None):
            t = ''
            for k, v in tycoon_file['Counts'].items(): t += f'{k}: {" "*(20 - len(k) - len(str(v)))}{math.floor(v)}\n'
            await tycoon_info['Tmessage'].edit(
                embed=discord.Embed(
                        color=0x08c912,
                        title=':coin:ステータス:credit_card:',
                        description=f'{t}{"-"*22}\n{tycoon_file["Points"]:>20,}P\n`開始時刻: {tycoon_file["start_date"]}`'
                )
            )

        def save(self, guild_id, tycoon_file, tycoon_info, *, message=None):
            tycoon_address = f'./db/tycoon/{guild_id}.json'
            with open(tycoon_address, mode='w', encoding='utf-8') as f:
                json.dump(tycoon_file, f, indent=4)


    othello_body = _othello_body_()
    tycoon = _tycoon_()



    @client.event
    async def on_ready():
        '''
        threading.Thread(target=send_message()).start()
        send_message()
        '''
        tycoon_RegPro.start()
        print(f'Ready to HacGame_onDiscord(Python) v{VERSION} Bot')
        print()

    @client.event
    async def on_message(message):
        def message_log(content):
            date = datetime.datetime.now()
            print(Color.GREEN +'-'+ str(date) +'-'+ Color.END)
            print(' チャンネル: ' + message.channel.name)
            print(' 送信者: ' + message.author.name)
            print(' メッセージ: ' + message.content)
            print(' 実行結果: '+ content)
            print()

        content = str(message.content).split()
        date_t = datetime.date.today()

        date = datetime.datetime.now()
        print(f'Message detected-> -{date.hour}:{str(date.minute).zfill(2)}:{str(date.second).zfill(2)}-{message.channel.name}.{message.author}: {message.content}')
        # if len(db['messages']) >= 10: db['messages'].pop()
        # db['messages'].append(message.content)

        if (len(content) < 1): # ※文字コンテンツがなければ処理されない
            return

        if (content[0] == PREFIX): # 接頭辞コマンド
            if (True): # 通常コマンド
                if (content[1] == 'test'):
                    message_log('テスト')

                elif content[1] == 'ping':
                    pass
                    # await message.channel.send(f'Pong! `{client.ws.}ms`')

                elif content[1] == 'help':
                    pass

                elif str(content[1]).lower() in ('identityv', 'iv') and str(content[2]).lower() == 'rank':
                    content = [i.lower() for i in content]
                    data = None
                    rec_address = './db/IdentityV/Rank_record.json'
                    with open(rec_address, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    if str(date_t) not in data['record']:
                        data['record'][str(date_t)] = {"win": 0, "draw": 0, "lose": 0, "comment": ""}

                    if len(content) <= 3 or content[3] == 'help':
                        await message.channel.send(None, 
                            embed=discord.Embed(
                                color=0xedde11,
                                title='試作第五人格記録表コマンド`_cd IdentityV(iv) rank ...`',
                                description='`add <w, d, l>`: その日の記録に<勝,分,敗>いずれかのカウントを追加します。\n \
                                            `comment <コメント>`: その日の記録にコメントを残します。すでにコメントがある場合、新しく入力したコメントで上書きされます。\n \
                                            `help`: この説明を表示します。\n \
                                            `print [日付]`: 合計記録とそれに関する情報を表示します。[日付]に「例: `2099-12-31`」記録・更新された日付を入力するとその日までの記録として計算・表示します。\n \
                                            `set <勝> <分> <敗>`: その日の記録を書き換えます。 「`*`」を入力することでその位置の記録を保持することができます。\n \
                                            `更新日時: 2021/07/19 21:02`'
                            )
                        )
                        message_log(f'-IdentityV ランクマ記録- 説明書表示')

                    if content[3] == 'add':
                        if content[4] in ('w', 'win'):
                            data['record'][str(date_t)]['win'] += 1
                        elif content[4] in ('d', 'draw'):
                            data['record'][str(date_t)]['draw'] += 1
                        elif content[4] in ('l', 'lose'):
                            data['record'][str(date_t)]['lose'] += 1
                        with open(rec_address, 'w') as f:
                            json.dump(data, f, indent=4)
                        await message.channel.send('{w}/{d}/{l}'.format(w=data['record'][str(date_t)]['win'], d=data['record'][str(date_t)]['draw'], l=data['record'][str(date_t)]['lose']))
                    
                    elif content[3] == 'set':
                        Err_flag = False
                        def set_rec(num, setting):
                            data['record'][str(date_t)][setting] = num
                        for i in range(3):
                            if content[i+4] in ('*', ''):
                                continue
                            try:
                                if int(content[i+4]) < 0:
                                    await message.channel.send('**※0を下回る値は入力(記録)できません。**')
                                    message_log(Color.RED +'[エラー] -IdentityV ランクマ記録- 入力エラー(content < 0)'+ Color.END)
                                    Err_flag = True
                                    break
                            except:
                                await message.channel.send('**※0以上の値を入力してください。**')
                                message_log(Color.RED +'[エラー] -IdentityV ランクマ記録- 入力エラー(数字以外入力)'+ Color.END)
                                Err_flag = True
                                break
                            if i==0: set_rec(int(content[i+4]), 'win')
                            elif i==1: set_rec(int(content[i+4]), 'draw')
                            elif i==2: set_rec(int(content[i+4]), 'lose')

                        try:
                            if Err_flag == False:
                                with open(rec_address, 'w') as f:
                                    json.dump(data, f, indent=4)
                                await message.channel.send(f'今日の記録を`{content[4]}/{content[5]}/{content[6]}`に書き換え/変更しました。')
                                message_log(f'-IdentityV ランクマ記録- 本日記録書き換え => {content[4]}/{content[5]}/{content[6]}')
                        except:
                            pass

                    elif content[3] == 'print':
                        if len(content) > 4: date_t = content[4] # 日にちの指定がある場合、上書きする。

                        total, percent = [0, 0, 0], [0, 0, 0]
                        for i in data['record'].values():
                            total[0] += i['win']
                            total[1] += i['draw']
                            total[2] += i['lose']
                            if i == date_t: break
                        
                        all_total = sum(total)
                        try:
                            test = data["record"][str(date_t)] # 指定された日にちでデータを参照できるかの確認
                            for i in range(3):
                                percent[i] = math.floor(total[i] / all_total * 10000)/100
                        except:
                            await message.channel.send('**※[エラー]データが存在しないか存在しないデータを参照しようとしています。**')
                            message_log(Color.RED +'[エラー] -IdentityV ランクマ記録- データなし'+ Color.END)

                        else:
                            await message.channel.send(f'{data["title"]}\n\n{str(date_t).replace("-", "/")}更新\n' + 
                                f'\n{data["record"][str(date_t)]["comment"]}\n' + 
                                f'\n勝ち⭕️{total[0]}(+{data["record"][str(date_t)]["win"]}) [{percent[0]}%]' + 
                                f'\n負け:cyclone:{total[2]}(+{data["record"][str(date_t)]["lose"]}) [{percent[2]}%]' + 
                                f'\n分け:eight_spoked_asterisk:{total[1]}(+{data["record"][str(date_t)]["draw"]}) [{percent[1]}%]')
                            message_log('-IdentityV ランクマ記録- まとめ出力完了')

                    elif content[3] == 'comment':
                        str_comment = ''
                        for i in content[4:]: str_comment += i + ' '
                        str_comment = str_comment.rstrip()
                        data['record'][str(date_t)]['comment'] = str_comment
                        with open(rec_address, 'w') as f:
                            json.dump(data, f, indent=4)
                        await message.channel.send(f'本日分の記録にコメントをしました。以下、内容↓\n{str_comment}')
                        message_log(('-IdentityV ランクマ記録- コメント'))


                elif content[1] == 'othello':
                    nonlocal othello

                    if len(content) == 2:
                        if othello['mode'] == "stand-by":
                            othello['players'] = [message.author.id]
                            othello['mode'] = "waiting"
                            await message.channel.send(None,
                                embed=discord.Embed(
                                    color=0x12990b,
                                    title=':black_circle:オセロ:white_circle:',
                                    description=f'**{message.author.nick}** がオセロの募集を開始しました。\n\
                                    20秒以内に`_pcd othello`を入力することで参加することが出来ます。\n\
                                    `_pcd othello helpでオセロ操作・ルールを確認できます。`\
                                    '
                                ))
                            message_log('コマンド: 送信者によりオセロの募集が開始されました。')
                            await asyncio.sleep(20)
                            if 2 <= len(othello['players']) <= 4:
                                txt_mem = ''
                                for i in othello['players']:
                                    User = await discord.Client.fetch_user(client, int(i))
                                    txt_mem += f'・{User.name}\n'
                                await message.channel.send(None,
                                    embed=discord.Embed(
                                        color=0x12990b,
                                        title=':white_check_mark::black_circle:オセロ:white_circle::white_check_mark:',
                                        description=f'[参加者リスト]\n{txt_mem}**まもなくオセロが開始されます。**'
                                    ))
                                message_log('成功: オセロ開始前状態に移行')
                                await asyncio.sleep(3)
                                othello['mode'] = "playing"
                                await othello_body.start(message)


                            else:
                                await message.channel.send(None,
                                    embed=discord.Embed(
                                        color=0x12990b,
                                        title=':x::black_circle:オセロ:white_circle::x:',
                                        description=f'**オセロの開催に失敗、もしくは人数が足りませんでした。**'
                                    ))
                                message_log('失敗: オセロ開始失敗')
                                othello_body._othello_init_()


                        elif othello['mode'] == "waiting":
                            if message.author.id not in othello['players']:
                                othello['players'].append(message.author.id)
                                await message.channel.send(None,
                                    embed=discord.Embed(
                                        color=0x12990b,
                                        title=':new::black_circle:オセロ:white_circle::new:',
                                        description=f'**{message.author.name}**が新たにオセロに参加しました。'
                                    ))
                                message_log('成功: 送信者がオセロに参加しました。')
                            else:
                                await message.channel.send('**※あなたはすでに参加しています。**')
                                message_log(Color.YELLOW + 'エラー: オセロ参加失敗(既に参加済みのプレイヤー)' + Color.END)

                    elif content[2] == 'help':
                        await message.channel.send(None,
                            embed=discord.Embed(
                                color=0x12990b,
                                title=':book::black_circle:オセロ・ルール:white_circle::book:',
                                description='**[開始方法]**\n1. 「`_pcd othello`」と入力しオセロ参加者を募集する。\n2. 参加希望者は同じくコマンドを入力し参加する。(4人まで)\n3. 一定時間経過後開始される。\n**[遊び方]**\n1. 自分の出番になったら座標指定「`<アルファベット> <数字>`」で交わる位置に置くことが出来ます。\n2. 石は自分のものでない限り色を関係なく挟むことが出来ます。また、置ける場所は黄色でハイライトされます。\n**[コマンド]**\n`recall`: オセロの盤面を呼び戻すことが出来ます。'
                            ))

                    elif content[2] == 'status':
                        await message.channel.send(f'モード: `{othello["mode"]}`')

                elif content[1] == 'rand': # テスト(ランダム数値出すやつ)
                    rand_mess = await message.channel.send('---')
                    times = 5
                    if len(content) > 2: 
                        if int(content[2]) <= 25: times = int(content[2])
                        else: times = 5
                    for _ in range(times):
                        await asyncio.sleep(0.025)
                        await rand_mess.edit(content='{:0=3}'.format(math.floor(random.random()*1000)))

                elif content[1] == 'tycoon': # Discord_Tycoon
                    tycoon_address = f'./data/tycoon/{message.guild.id}.json'

                    if content[2] == 'create':
                        if Path.isfile(tycoon_address):
                            await message.channel.send('**[エラー] ※既にデータが存在しているため作成・構築することが出来ません。**')
                            message_log(Color.RED + '[DiscordTycoon: エラー] チャンネル/データ作成失敗(既存データ存在)' + Color.END)
                            return
                        try:
                            Channel = await message.guild.create_text_channel('ポイント')
                            embed_id = await Channel.send(None, 
                                embed=discord.Embed(
                                    color=0x08c912,
                                    title=':coin:ステータス:credit_card:',
                                    description=f'Loading...'
                                )
                            )
                            embed_id = embed_id.id
                            data = {
                                    'guild_id': message.guild.id,
                                    'channel_id': Channel.id,
                                    'embed_id': embed_id,
                                    'Init_Server_name': message.guild.name,
                                    'start_date': datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                                    'Points': 0,
                                    'Counts': {}
                                   }
                            with open(tycoon_address, mode='x', encoding='utf-8') as f:
                                json.dump(data, f, indent=4)
                        except:
                            await message.channel.send('**[警告] ※チャンネル作成に失敗したか、データの新規作成に失敗した可能性があります。**')
                            message_log(Color.YELLOW + '[DiscordTycoon: 警告] チャンネル/データ作成失敗' + Color.END)
                        else:
                            await message.channel.send('**:white_check_mark:[成功] 当ギルド(サーバー)でのDiscordTycoonの構築に成功しました。**')
                            message_log(Color.GREEN + '[DiscordTycoon: 成功] チャンネル/データ構築完了' + Color.END)


            if (message.author.id == Owner["id"]): # オーナーコマンド
                if (content[1] == 'say'):
                    print('送信する内容を入力してください...')
                    await message.channel.send(input())

                elif (content[1] == 'timer'):
                    pass


        if not content[0] == PREFIX and othello['mode'] == "playing" and message.channel.id == othello['Use_channel'].id:
            if message.author.id == othello['players'][othello['turn']] and len(content) >= 2 and not message.author == client:
                await othello_body.put(message, content[0], content[1], othello['stones'][othello['turn']])
                await message.delete()
            elif content[0] == 'recall':
                text = othello_body.print()
                player = await discord.Client.fetch_user(client, othello["players"][othello["turn"]])
                othello['Embed_info'] = await message.channel.send(None,
                    embed=discord.Embed(
                        color=0x12990b,
                        title=':arrow_forward::black_circle:オセロ:white_circle::arrow_forward:',
                        description=f':{othello["format"][othello["stones"][othello["turn"]]]}:**{player}** の番`{othello["turn_count"]}巡目{othello["turn"]+1}人目`\n' + text + othello['description']['how2put']
                    )
                )
                await message.delete()


        tycoon_file, tycoon_info = await tycoon.load(message.guild.id)

        if tycoon_file: # tycoonファイルが存在する場合有効
            def message_point(points):
                tycoon_file['Points'] += points
                tycoon_file['Counts'].setdefault('message', 0)
                tycoon_file['Counts']['message'] += 1

            message_point(1)

            tycoon.save(message.guild.id, tycoon_file, tycoon_info)
            await tycoon.print(tycoon_file, tycoon_info)


    @tasks.loop(seconds=6)
    async def tycoon_RegPro():
        tycoon_file, tycoon_info = await tycoon.load(713785498660766028) # 現在1チャンネル(葱鮪)のみ

        def leaving_point(points):
            tycoon_file['Points'] += points
            tycoon_file['Counts'].setdefault('leaving_m', 0)
            tycoon_file['Counts']['leaving_m'] += 0.1

            tycoon_file['Points'] = round(tycoon_file['Points']*10) / 10
            tycoon_file['Counts']['leaving_m'] = round(tycoon_file['Counts']['leaving_m']*10) / 10

        leaving_point(0.1)
        
        tycoon.save(713785498660766028, tycoon_file, tycoon_info)
        await tycoon.print(tycoon_file, tycoon_info)



    client.run(TOKEN)




def _tkinter_():
    async def text_submit(id, text):
        Channel = await discord.Client.get_user(id)
        await Channel.send(text)
        print('---送信しました---')


    root = tk.Tk()
    root.title('[Test] Python Discord bot with Tkinter')
    root.minsize(width=360, height=240)
    root.geometry("720x480")


    channelID = tk.IntVar()
    textContent = tk.StringVar()

    channelID_label = tk.Label(root, text="ChannelID:")
    channelID_label.place(x=10, y=10)
    channelID_entry = tk.Entry(root, width=30, justify="right", textvariable=channelID)
    channelID_entry.place(x=80, y=10)
    content_label = tk.Label(root, text="Content:")
    content_label.place(x=10, y=34)
    content_entry = tk.Entry(root, width=48, textvariable=textContent)
    content_entry.place(x=80, y=34)
    submit_button = tk.Button(root, text="Submit", command=lambda: text_submit(channelID.get(), textContent.get()))
    submit_button.place(x=380, y=34)
    chat_log_text = tk.Text(root, width=40, height=10)
    chat_log_text.place(x=20, y=100)

    # for i in len(db['messages']):
    #     chat_log_text.insert(float(i+1.0), f'{db["messages"][i]}\n')

    run_button = tk.Button(root, text="Run Discord", command=lambda: print(f'ID: {channelID.get()}\nText: {textContent.get()}'))
    run_button.pack(anchor=tk.SE, side=tk.BOTTOM)
    root.mainloop()



threading.Thread(target=_discord_).start()
# threading.Thread(target=_tkinter_).start()

# client.loop.create_task(_tkinter_())