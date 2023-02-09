import discord
import asyncio
import datetime
import os

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="サーバー死活監視中"))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----')
    # メッセージIDを取得
    message_id = 00000000000000
    while True:
        # サーバーリストを取得
        server_list = []
        with open("server_list.txt") as f:
            for line in f:
                # 1行ずつサーバー情報を保存
                server_name, server_ip = line.split(",")
                server_list.append((server_name, server_ip))

        # サーバー毎にpingを行い結果を取得
        ping_results = []
        for server_name, server_ip in server_list:
            response = os.system(f"ping {server_ip}")
            # 取得した結果を変数に代入
            if response == 0:
                ping_status = "✅UP"
                color = 0x00FF00
            else:
                ping_status = "🛑DOWN"
                color = 0xFF0000
            ping_results.append((server_name, ping_status, color))

        # 現在時刻を取得
        now = datetime.datetime.now()
        # 日本時間に変換
        tokyo = datetime.timezone(datetime.timedelta(hours=9))
        now_tokyo = now.astimezone(tokyo)
        # 現在時刻を文字列に変換
        now_time = now_tokyo.strftime("%Y/%m/%d %H:%M:%S")

        # embed表示用にデータを整形
        embed_data = discord.Embed(
            title="サーバー死活監視",
            description="監視情報一覧",
        )
        # 結果をFieldsに追加
        for server_name, ping_status, color in ping_results:
            embed_data.add_field(name=server_name, value=ping_status, inline=True)
        embed_data.set_footer(text="Updated: " + now_time)

        # チャンネルを取得
        channel = client.get_channel(000000000000000)
        # メッセージが存在するか確認
        message = None
        try:
            message = await channel.fetch_message(message_id)
        except discord.errors.NotFound:
            # 存在しない場合は新しく投稿
            message = await channel.send(embed=embed_data)
            message_id = message.id
        else:
            # 存在する場合は編集
            # サーバー毎の結果によってエンベッドの色を変更
            # DOWNが一つでもあれば赤色をセット
            color = 0x00FF00
            for _, ping_status, _ in ping_results:
                if ping_status == "🛑DOWN":
                    color = 0xFF0000
                    break
            embed_data.color = color
            await message.edit(embed=embed_data)

        # 30秒待機
        await asyncio.sleep(30)

@client.event
async def on_message(message):
    if message.content.startswith("!server_add"):
        # コマンドを分割
        command = message.content.split(" ")
        if len(command) == 3:
            # コマンドからサーバー名とipアドレスを取得
            server_name = command[1]
            server_ip = command[2]
            # 追加するサーバー情報を保存
            with open("server_list.txt", "a") as f:
                f.write(server_name + "," + server_ip + "\n")
            # ユーザーに反応
            await message.channel.send("サーバーを追加しました！")
        else:
            # ユーザーに反応
            await message.channel.send("サーバー名とIPアドレスを入力してください！")
    
    if message.content.startswith("!server_remove"):
        # コマンドを分割
        command = message.content.split(" ")
        if len(command) == 2:
            # コマンドからサーバー名を取得
            server_name = command[1]
            # 全てのサーバー情報を取得
            server_list = []
            with open("server_list.txt") as f:
                for line in f:
                    # 1行ずつサーバー情報を保存
                    server_name_2, server_ip = line.split(",")
                    server_list.append((server_name_2, server_ip))
            # 削除対象のサーバー情報を取得
            remove_server = None
            for server in server_list:
                if server[0] == server_name:
                    remove_server = server
                    break
            else:
                # ユーザーに反応
                await message.channel.send("サーバーが存在しません！")
            # 削除対象のサーバー情報が存在する場合
            if remove_server != None:
                # サーバー情報をファイルから削除
                with open("server_list.txt", "r") as f:
                    lines = f.readlines()
                with open("server_list.txt", "w") as f:
                    for line in lines:
                        if remove_server[0]+","+remove_server[1] not in line:
                            f.write(line)
                # ユーザーに反応
                await message.channel.send("サーバーを削除しました！")
        else:
            # ユーザーに反応
            await message.channel.send("サーバー名を入力してください！")

client.run("トークンをここに入れてください")