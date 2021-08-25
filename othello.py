# -*- coding: utf-8 -*-

mode = 'start'
Game_Board = [[0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 2, 0, 0, 0],
              [0, 0, 0, 2, 1, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              ]


def put(stone):
    pos = input().split()
    pos[0] = int(pos[0], base=18)-9
    pos[1] = int(pos[1])
    pos = [pos[1]-1, pos[0]-1] # 配列で管理する都合でx, y座標を逆転させ、互いに-1しています。
    # print(pos)
    target = []

    if Game_Board[pos[0]][pos[1]] != 0:
        return 'Failed'

    for i in ((-1,-1), (-1,0), (-1,+1), (0,-1), (0,+1), (+1,-1), (+1,0), (+1,+1)): # 検索順: 左上、上、右上、左、右、左下、下、右下
        search = pos[:]
        temp_targ = []
        while True:
            search[0], search[1] = search[0]+i[0], search[1]+i[1]
            if not 0 <= search[0] <= 7 or not 0 <= search[1] <= 7 or Game_Board[search[0]][search[1]] == 0: # 挟み込み失敗時
                break
            elif Game_Board[search[0]][search[1]] == stone: # 検索場所が自分の石である時
                for j in temp_targ:
                    target.append(j)
                break
            else: # それ以外(検索場所が相手の石である時)
                temp_targ.append([search[0], search[1]])
                # continue

    if len(target) > 0: # 置ける場所であるかの最終的な判定
        Game_Board[pos[0]][pos[1]] = stone
    else:
        return 'Failed'

    for i in target:
        Game_Board[i[0]][i[1]] = stone

def place_check(stone): # stone: チェックする石の種類を入力してください。, /, *
    can_place = []
    for x in range(8):
        for y in range(8):
            pos = [y, x]

            if Game_Board[pos[0]][pos[1]] != 0:
                continue

            for i in ((-1,-1), (-1,0), (-1,+1), (0,-1), (0,+1), (+1,-1), (+1,0), (+1,+1)): # 検索順: 左上、上、右上、左、右、左下、下、右下
                search = pos[:]
                temp_targ = []
                break_flag = False
                while True:
                    search[0], search[1] = search[0]+i[0], search[1]+i[1]
                    if not 0 <= search[0] <= 7 or not 0 <= search[1] <= 7 or Game_Board[search[0]][search[1]] == 0: # 挟み込み失敗時
                        break
                    elif Game_Board[search[0]][search[1]] == stone: # 検索場所が自分の石である時
                        if len(temp_targ) >= 1:
                            can_place.append(pos)
                            break_flag = True
                        break
                    else: # それ以外(検索場所が相手の石である時)
                        temp_targ.append([search[0], search[1]])
                        # continue

                if break_flag == True:
                    break
    return can_place


while True:
    turn = [1, 2]
    for i in turn:
        place_check('temp')
        put(i)
        for j in range(8): print(str(Game_Board[j]))
        print('\n')