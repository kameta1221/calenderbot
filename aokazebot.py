import asyncio
import datetime
import html
import json
import os
import random
import re
import sys
from typing import get_args
from urllib import request

import discord
import gspread
import requests
import wanakana
from discord import embeds
from discord.ext import commands, pages, tasks
from discord.ext.commands import context
from discord.ext.commands.core import command
from discord.player import FFmpegPCMAudio
from discord.ui import Button, View
from google.cloud import texttospeech, translate
from ibm_cloud_sdk_core import authenticators
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1
from oauth2client.service_account import ServiceAccountCredentials
from requests.api import delete
from sqlalchemy import Column, Integer, String, create_engine, orm
from sqlalchemy.ext.declarative import declarative_base

TOKEN = os.environ['DISCORD_BOT_TOKEN']
DATABASE_URL = os.environ['DATABASE_URL'].replace("postgres", "postgresql")
TALK_API = os.environ['TALK_API_KEY']
TALK_API_URL = os.environ['TALK_API_URL']
IBM_TTS_KEY = os.environ['IBM_TTS_KEY']
IBM_URL = os.environ['IBM_URL']
SPREADSHEET_JSON = os.environ['SPREADSHEET_JSON']
SPREADSHEET_KEY = os.environ['SPREADSHEET_KEY']
YAHOO_API_URL = os.environ['YAHOO_API_URL']
YAHOO_API_KEY = os.environ['YAHOO_API_KEY']
VOICEVOX_HOST = os.environ['VOICEVOX_HOST']
VOICEVOX_PORT = os.environ['VOICEVOX_PORT']
VOICEVOX_API_KEY = os.environ['VOICEVOX_API_KEY']


# postgre
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)

# ibm_tts
ibm_tts = TextToSpeechV1(IAMAuthenticator(IBM_TTS_KEY))
ibm_tts.set_service_url(IBM_URL)

discord_intents = discord.Intents.all()
bot = commands.Bot(command_prefix="！",
                   intents=discord_intents, help_command=None)

vc = {}
tc = {}
order = []
who = 1
botti = True
entry_and_exit = True
talk = False
colo = False
calibration = False
translation = False
target_language_num = 2
target_language_code = ["zh-CN","zh-TW","en","fr","de","ja","ko","ru"]


dayformat = '%Y年%m月%d日 %H:%M:%S'
weekformat = '%Y年%m月%d日'

inmsg = ['まーた喋太郎パイセンさぼりっすかぁｗｗ', 'もういい！！俺が行く！！', '俺自身がーーー\n\n\tーーーーー喋太郎になることだ',
         '俺はガンダムで行く！', '(ﾋﾟｺﾝｯ)敵と交戦中', '喋太郎？知らんなぁ(笑)', 'まぁたあいるん戦犯寝落ちっすかwww',
         'オレオメガｶﾝﾄﾂ', '自慢じゃねぇが俺は100mを5秒フラットで走れるんだ', 'それは　まぎれもなく　ヤツさ', '卍解ッ！',
         '( ﾟдﾟ )( ﾟдﾟ )( ﾟдﾟ )( ﾟдﾟ )( ﾟдﾟ )( ﾟдﾟ )( ﾟдﾟ )( ﾟдﾟ )( ﾟдﾟ )', 'ソサの対混成はクソ','愛シテルの不発弾']
outmsg = ['おぅまたな！', 'さらだばー！！', 'あぁ…やっと寝れる', '疲れた…疲れたよパトラッシュ', 'あっちにサプライボックスがある',
          'うるせ～‼‼‼しらね～‼‼‼\nFAINALFANT\n                AGY', 'すこしやすませｓｔくｒえよ', '独立変数を設置する',
          '俺を置いて……先に行け', 'くぁｗせｄｒｆｔｇｙふじこｌｐ；＠：「」', 'キルリーダーを撃破した', '幸せの神様は泣き虫が嫌いなんだ',
          'ｵｲｵｲｵｲｵｲｵｲｵｲｵｲｵｲ', '(　ﾟдﾟ)(　ﾟдﾟ)(　ﾟдﾟ)(　ﾟдﾟ)(　ﾟдﾟ)(　ﾟдﾟ)(　ﾟдﾟ)(　ﾟдﾟ)(　ﾟдﾟ)',
          'あ❗️ ぬーわ❗️:new_moon_with_face:ダン:boom:ダン:boom:ダン:boom:シャーン:notes:ぬわ:full_moon_with_face:ぬわ:new_moon_with_face:ぬわ:full_moon_with_face:ぬわ:new_moon_with_face:ぬわ:full_moon_with_face:ぬわ:new_moon_with_face:ぬ〜〜〜わ:arrow_heading_up:ぬわ:new_moon_with_face:ぬわ:full_moon_with_face:ぬわ:new_moon_with_face:ぬわ:full_moon_with_face:ぬわ:new_moon_with_face:ぬわ:full_moon_with_face:ぬ～～～わ:arrow_heading_down::sun_with_face:']


speaker = ["ja-JP-Wavenet-A", "ja-JP-Wavenet-B",
           "ja-JP-Wavenet-C", "ja-JP-Wavenet-D", "ja-JP_EmiV3Voice",
           "四国めたん (あまあま)", "四国めたん (ノーマル)", "四国めたん (セクシー)", "四国めたん (ツンツン)",
           "ずんだもん (あまあま)", "ずんだもん (ノーマル)", "ずんだもん (セクシー)", "ずんだもん (ツンツン)",
           "春日部つむぎ", "波音リツ", "雨晴はう"]
embedcolor = [0x44ff44, 0xffd000, 0xff6600, 0x990000, 0xff0000]


class Ideyo(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Yaruki())
        self.add_item(Abayo())
        self.add_item(Help())
        self.add_item(Talk())
        self.add_item(Yourname())
        self.add_item(Translation())
        self.add_item(Speaker())


class SpeakerList(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Speaker())


class Speaker(discord.ui.Select):
    def __init__(self):
        options = []
        options.append(discord.SelectOption(
            label=speaker[0], description='圧倒的美少女'))
        options.append(discord.SelectOption(
            label=speaker[1], description='不動の人気No.1'))
        options.append(discord.SelectOption(
            label=speaker[2], description='くそ雑魚ナメクジ'))
        options.append(discord.SelectOption(
            label=speaker[3], description='オジサン'))
        options.append(discord.SelectOption(
            label=speaker[4], description='新入り！'))
        options.append(discord.SelectOption(
            label=speaker[5], description='はっきりした芯のある声'))
        options.append(discord.SelectOption(
            label=speaker[6], description='はっきりした芯のある声'))
        options.append(discord.SelectOption(
            label=speaker[7], description='はっきりした芯のある声'))
        options.append(discord.SelectOption(
            label=speaker[8], description='はっきりした芯のある声'))
        options.append(discord.SelectOption(
            label=speaker[9], description='子供っぽい高めの声'))
        options.append(discord.SelectOption(
            label=speaker[10], description='子供っぽい高めの声'))
        options.append(discord.SelectOption(
            label=speaker[11], description='子供っぽい高めの声'))
        options.append(discord.SelectOption(
            label=speaker[12], description='子供っぽい高めの声'))
        options.append(discord.SelectOption(
            label=speaker[13], description='元気な明るい声'))
        options.append(discord.SelectOption(
            label=speaker[14], description='低めのクールな声'))
        options.append(discord.SelectOption(
            label=speaker[15], description='優しく可愛い声'))

        super().__init__(placeholder='キャラクターセレクト',
                         min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global who
        await interaction.response.send_message(f'{interaction.user.name}が{self.values[0]}にボイチェンしたで！')
        for num in range(len(speaker)):
            if self.values[0] == speaker[num]:
                who = num
                break


class language_codeList(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(language_code())


class language_code(discord.ui.Select):
    def __init__(self):
        options = []
        options.append(discord.SelectOption(
            label=target_language_code[0], description='中国語（簡体）'))
        options.append(discord.SelectOption(
            label=target_language_code[1], description='中国語（繁体）'))
        options.append(discord.SelectOption(
            label=target_language_code[2], description='英語'))
        options.append(discord.SelectOption(
            label=target_language_code[3], description='フランス語'))
        options.append(discord.SelectOption(
            label=target_language_code[4], description='ドイツ語'))
        options.append(discord.SelectOption(
            label=target_language_code[5], description='日本語'))
        options.append(discord.SelectOption(
            label=target_language_code[6], description='韓国語'))
        options.append(discord.SelectOption(
            label=target_language_code[7], description='ロシア語'))
        super().__init__(placeholder='target_language',min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global target_language_num
        await interaction.response.send_message(f'{self.values[0]}に翻訳するで！')
        for num in range(len(target_language_code)):
            if self.values[0] == target_language_code[num]:
                target_language_num = num
                break


class AreasList(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(AreasSelect())


class AreasSelect(discord.ui.Select):

    def __init__(self):
        options = []
        areas = ["釧路", "旭川", "札幌", "青森", "秋田", "仙台", "新潟", "金沢", "東京", "宇都宮",
                 "長野", "名古屋", "大阪", "高松", "松江", "広島", "高知", "福岡", "鹿児島", "奄美", "那覇", "石垣"]
        for area in areas:
            options.append(discord.SelectOption(label=area, description=''))

        super().__init__(placeholder='地名', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        url = 'https://www.jma.go.jp/bosai/forecast/data/forecast/010000.json'
        filename = 'tenki.json'
        request.urlretrieve(url, filename)
        with open('tenki.json', 'r', encoding="UTF-8") as f:
            data = json.load(f)

        await interaction.response.send_message(f"[ {self.values[0]} ] の天気予報やで", ephemeral=True)
        await interaction.response.send_message(embed=forecast_weathers(self.values[0], data), ephemeral=True)
        await interaction.response.send_message(embed=forecast_winds(self.values[0], data), ephemeral=True)
        await interaction.response.send_message(embed=forecast_pops(self.values[0], data), ephemeral=True)
        await interaction.response.send_message(embed=forecast_temps(self.values[0], data), ephemeral=True)
        await interaction.response.send_message(embed=forecast_overview(self.values[0], data), ephemeral=True)


class BottiButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(BottiOn())
        self.add_item(BottiOff())


class BottiOn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ON", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        global botti
        botti = True
        await interaction.response.send_message(f'{self.label}にしたで！')


class BottiOff(discord.ui.Button):
    def __init__(self):
        super().__init__(label="OFF", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        global botti
        botti = False
        await interaction.response.send_message(f'{self.label}にしたで！')


class TalkSwitchButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(TalkOn())
        self.add_item(TalkOff())


class TalkOn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ON", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        global talk
        talk = True
        await interaction.response.send_message(f'{self.label}にしたで！')


class TalkOff(discord.ui.Button):
    def __init__(self):
        super().__init__(label="OFF", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        global talk
        talk = False
        await interaction.response.send_message(f'{self.label}にしたで！')


class ColoSwitchButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ColoOn())
        self.add_item(ColoOff())


class ColoOn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ON", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        global colo
        colo = True
        await interaction.response.send_message(f'{self.label}にしたで！')


class ColoOff(discord.ui.Button):
    def __init__(self):
        super().__init__(label="OFF", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        global colo
        colo = False
        await interaction.response.send_message(f'{self.label}にしたで！')


class YournameSwitchButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(NameOn())
        self.add_item(NameOff())


class NameOn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ON", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        global entry_and_exit
        entry_and_exit = True
        msg = ['「大事な人。忘れたくない人。忘れちゃダメな人。誰だ、誰だ、誰だ？名前は！」',
               '「君の、名前はーー」', '「私たちは、会えば絶対、すぐにわかる。」']
        await interaction.response.send_message(random.choice(msg))


class NameOff(discord.ui.Button):
    def __init__(self):
        super().__init__(label="OFF", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        global entry_and_exit
        entry_and_exit = False
        await interaction.response.send_message(f'「これじゃ…名前、わかんないよ」')


class TranslationSwitchButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(TranslationOn())
        self.add_item(TranslationOff())


class TranslationOn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ON", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        global translation
        translation = True
        await interaction.response.send_message(f'{self.label}にしたで！',view=language_codeList())


class TranslationOff(discord.ui.Button):
    def __init__(self):
        super().__init__(label="OFF", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        global translation
        translation = False
        await interaction.response.send_message(f'{self.label}にしたで！')


class HelpButton(discord.ui.View):
    def __init__(self, args):
        super().__init__()

        for txt in args:
            self.add_item(Help(txt))


class Help(discord.ui.Button):
    def __init__(self):
        super().__init__(label="！へるぷ", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        helpemb = discord.Embed(
            title="あおかぜぼっと速報", description="こまんどせつめい", color=0x0000ff)
        helpemb.set_author(name=interaction.user.display_name,
                           icon_url=interaction.user.display_avatar)
        helpemb.add_field(name=":one:　`！いでよ`",
                          value="> 読み上げを開始するで", inline=False)
        helpemb.add_field(name=":two:　`！あばよ`",
                          value="> 読み上げを終了するで", inline=False)
        helpemb.add_field(name=":three:　`！だまれ`",
                          value="> 読み上げを中断するで", inline=False)
        helpemb.add_field(name=":four:　`！やるき`",
                          value="> ぼっとのやるき、声の担当がわかるで", inline=False)
        helpemb.add_field(name=":five:　`！ぼいちぇん`",
                          value="> 読み上げる声をカエルで", inline=False)
        helpemb.add_field(name=":six:　`！へるぷ`",
                          value="> いま使ったやろ！？", inline=False)
        helpemb.add_field(name=":seven:　`！じしょ`",
                          value="> 登録した単語がみれるで", inline=False)
        helpemb.add_field(name=":eight:　`！ついか` <単語> <呼び方>",
                          value=">>> <単語>を<呼び方>で読むで\n 例）`！ついか`　蒼風　あおかぜ", inline=False)
        helpemb.add_field(name=":nine:　`！さくじょ` <番号>",
                          value=">>> 登録された単語を削除するで\n`！じしょ`で削除する単語の番号を確認してな", inline=False)
        helpemb.add_field(name=":keycap_ten:　`！ばくだん` <レベル>",
                          value=">>> マインスイーパであそべるで\nレベルは1～10まであるで", inline=False)
        helpemb.add_field(name=":one::one:　`！てんき` <地名>",
                          value=">>> <地名>の天気予報が見れるで", inline=False)
        helpemb.add_field(name=":one::two:　`！きみのなは`",
                          value=">>> VCに入ってきたやつの名前を読み上げるで", inline=False)
        helpemb.add_field(name=":one::three:　？？？",
                          value=">>> おっと？こっからさきはまだ製作中や", inline=False)
        helpemb.add_field(name=":arrow_forward:　`そのた`",
                          value=">>> たまに読み上げさぼるで~~喋太郎ほどじゃないけど笑~~\nそんなときは`！やるき`を確認してみてな", inline=False)
        helpemb.add_field(name=":arrow_forward:　`そのた２`",
                          value=">>> 質問・要望は<@!614978622104666190>に言ってな\n気分次第で返事してくれるで", inline=False)
        helpemb.set_footer(text="Last update ~> 2021/11/30")
        await interaction.response.send_message(f'{interaction.user.display_name}にだけこそっと教えるで', embed=helpemb, ephemeral=True)


class AbayoButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Abayo())


class Abayo(discord.ui.Button):
    def __init__(self):
        super().__init__(label="！あばよ", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        if vc[interaction.guild.id].is_connected:
            print("read_stop!!")
            vc[interaction.guild.id].stop()
            await vc[interaction.guild.id].disconnect()
            print(get_now().strftime(dayformat))
            await interaction.response.send_message(embed=make_emb(bot.latency * 1000, ":mute: 読み上げ終了", interaction.user.display_name, interaction.user.display_avatar))
            return
        else:
            await interaction.response.send_message('読み上げてないで！？')


class YarukiButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Yaruki())


class Yaruki(discord.ui.Button):
    def __init__(self):
        super().__init__(label="！やるき", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=make_emb(bot.latency * 1000, ":muscle: やるきちぇっく", interaction.user.display_name, interaction.user.display_avatar))


class TalkButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Talk())


class Talk(discord.ui.Button):
    def __init__(self):
        super().__init__(label="！とーく", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("トーク機能を…？", view=TalkSwitchButton())


class Yourname(discord.ui.Button):
    def __init__(self):
        super().__init__(label="！君の名は", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("『君の名は』機能を…？", view=YournameSwitchButton())


class Translation(discord.ui.Button):
    def __init__(self):
        super().__init__(label="！ほんやく", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("ほんやく機能を…？", view=TranslationSwitchButton())


async def is_owner(ctx):
    return ctx.author.id == 614978622104666190


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}({bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="SINoALICE ━シノアリス━", type=1))
    print(discord.__version__)


@bot.command()
@commands.check(is_owner)
async def exit(ctx):
    await ctx.send('ﾉｼ')
    sys.exit()


@bot.command(name="ぼいちぇん")
async def voice_change(ctx):
    await ctx.send('誰と代わるかい？', view=SpeakerList(), delete_after=120)


# @bot.command(name="ぬーわ")
# async def nuwa(ctx):
#     await ctx.send('あ❗️ ぬーわ❗️:new_moon_with_face:ダン:boom:ダン:boom:ダン:boom:シャーン:notes:ぬわ:full_moon_with_face:ぬわ:new_moon_with_face:ぬわ:full_moon_with_face:ぬわ:new_moon_with_face:ぬわ:full_moon_with_face:ぬわ:new_moon_with_face:ぬ〜〜〜わ:arrow_heading_up:ぬわ:new_moon_with_face:ぬわ:full_moon_with_face:ぬわ:new_moon_with_face:ぬわ:full_moon_with_face:ぬわ:new_moon_with_face:ぬわ:full_moon_with_face:ぬ～～～わ:arrow_heading_down::sun_with_face:')
#     if ctx.message.guild:
#         if ctx.author.voice is None:
#             return
#     while ctx.guild.voice_client.is_playing():
#         await asyncio.sleep(0.1)
#     source = discord.PCMVolumeTransformer(
#         discord.FFmpegPCMAudio("sumo.mp3"), volume=0.25)
#     ctx.guild.voice_client.play(source)


@bot.command(name="ぼっち")
async def botti(ctx):
    await ctx.send("ボッチ機能を…？", view=BottiButton(), delete_after=120)


@bot.command(name="とーく")
async def talking(ctx):
    await ctx.send("トーク機能を…？", view=TalkSwitchButton(), delete_after=120)


@bot.command(name="ほんやく")
async def talking(ctx):
    await ctx.send("ほんやく機能を…？", view=TranslationSwitchButton(), delete_after=120)


@bot.command(name="ばくだん")
async def bomb(ctx, level: int):
    await ctx.send(minesweeper(level))


@bomb.error
async def bomb_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("使い方ちゃうで？　`！へるぷ`みてな？", delete_after=15)


@bot.command(name="へるぷ")
async def help_enb(ctx):
    helpemb = discord.Embed(
        title="あおかぜぼっと速報", description="こまんどせつめい", color=0x0000ff)
    helpemb.set_author(name=ctx.author.display_name,
                       icon_url=ctx.author.display_avatar)
    helpemb.add_field(name=":one:　`！いでよ`", value="> 読み上げを開始するで", inline=False)
    helpemb.add_field(name=":two:　`！あばよ`", value="> 読み上げを終了するで", inline=False)
    helpemb.add_field(name=":three:　`！だまれ`",
                      value="> 読み上げを中断するで", inline=False)
    helpemb.add_field(name=":four:　`！やるき`",
                      value="> ぼっとのやるき、声の担当がわかるで", inline=False)
    helpemb.add_field(name=":five:　`！ぼいちぇん`",
                      value="> 読み上げる声をカエルで", inline=False)
    helpemb.add_field(name=":six:　`！へるぷ`", value="> いま使ったやろ！？", inline=False)
    helpemb.add_field(name=":seven:　`！じしょ`",
                      value="> 登録した単語がみれるで", inline=False)
    helpemb.add_field(name=":eight:　`！ついか` <単語> <呼び方>",
                      value=">>> <単語>を<呼び方>で読むで\n 例）`！ついか`　蒼風　あおかぜ", inline=False)
    helpemb.add_field(name=":nine:　`！さくじょ` <番号>",
                      value=">>> 登録された単語を削除するで\n`！じしょ`で削除する単語の番号を確認してな", inline=False)
    helpemb.add_field(name=":keycap_ten:　`！ばくだん` <レベル>",
                      value=">>> マインスイーパであそべるで\nレベルは1～10まであるで", inline=False)
    helpemb.add_field(name=":one::one:　`！てんき` <地名>",
                      value=">>> <地名>の天気予報が見れるで", inline=False)
    helpemb.add_field(name=":one::two:　`！きみのなは`",
                      value=">>> VCに入ってきたやつの名前を読み上げるで", inline=False)
    helpemb.add_field(name=":one::three:　？？？",
                      value=">>> おっと？こっからさきはまだ製作中や", inline=False)
    helpemb.add_field(name=":arrow_forward:　`そのた`",
                      value=">>> たまに読み上げさぼるで~~喋太郎ほどじゃないけど笑~~\nそんなときは`！やるき`を確認してみてな", inline=False)
    helpemb.add_field(name=":arrow_forward:　`そのた２`",
                      value=">>> 質問・要望は<@!614978622104666190>に言ってな\n気分次第で返事してくれるで", inline=False)
    helpemb.set_footer(text="Last update ~> 2021/11/30")
    await ctx.send(embed=helpemb)


@bot.command(name="やるき")
async def yaruki(ctx):
    await ctx.channel.send(embed=make_emb(bot.latency * 1000, ":muscle: やるきちぇっく", ctx.author.display_name, ctx.author.display_avatar))


@bot.command(name="ころしあむ")
async def colosiam(ctx):
    await ctx.channel.send("コロシアム機能を…？", view=ColoSwitchButton(), delete_after=120)


@bot.command(name="きみのなは", aliases=['君の名は'])
async def yourname(ctx):
    await ctx.channel.send("『君の名は』機能を…？", view=YournameSwitchButton(), delete_after=120)


@bot.command(name="だまれ")
async def shut_up(ctx):
    global vc
    if vc[ctx.guild.id].is_playing():
        vc[ctx.guild.id].stop()
    else:
        await ctx.send("なんも言うてないやろが！？", delete_after=15)


@bot.command(name="いでよ")
async def come_on(ctx):
    global vc
    global tc
    if ctx.guild.id in vc:
        await vc[ctx.guild.id].disconnect()
        del vc[ctx.guild.id]
        del tc[ctx.guild.id]
    if ctx.message.guild:
        if ctx.author.voice is None:
            await ctx.send(ctx.author.mention+"お前VCおらんやん！", delete_after=15)
        else:
            if ctx.guild.voice_client:
                if ctx.author.voice.channel == ctx.guild.voice_client.channel:
                    await ctx.send('ちゃんとおるで！', delete_after=15)
                else:
                    await ctx.voice_client.disconnect()
                    await asyncio.sleep(0.5)
                    print(get_now().strftime(dayformat))
                    vc[ctx.guild.id] = await ctx.author.voice.channel.connect()
                    tc[ctx.guild.id] = ctx.channel.id
                    await ctx.send(embed=make_emb(bot.latency * 1000, ":loud_sound: 読み上げ開始", ctx.author.display_name, ctx.author.display_avatar), view=Ideyo())
                    await ctx.send(random.choice(inmsg))
            else:
                print(get_now().strftime(dayformat))
                vc[ctx.guild.id] = await ctx.author.voice.channel.connect()
                tc[ctx.guild.id] = ctx.channel.id
                await ctx.send(embed=make_emb(bot.latency * 1000, ":loud_sound: 読み上げ開始", ctx.author.display_name, ctx.author.display_avatar), view=Ideyo())
                await ctx.send(random.choice(inmsg))


@bot.command(name="あばよ")
async def good_bye(ctx):
    global vc
    global tc
    if vc[ctx.guild.id].is_connected:
        print("read_stop!!")
        vc[ctx.guild.id].stop()
        await vc[ctx.guild.id].disconnect()
        await ctx.send(embed=make_emb(bot.latency * 1000, ":mute: 読み上げ終了", ctx.author.display_name, ctx.author.display_avatar))
        await ctx.send(random.choice(outmsg))
    else:
        await ctx.send(ctx.author.mention+'読み上げてないで！？', delete_after=15)


@bot.command(name="ついか")
async def add_word(ctx, keyword: str, read: str):
    dict_add(keyword, read)
    words = dict_get()
    embed = discord.Embed(
        title="あおかぜぼっと速報", description="じしょいちらん", color=0x0000ff)
    embed.add_field(name='ばんごう', value='たんご：よみがな', inline=False)
    for i, word in enumerate(words, start=1):
        if i % 15 == 0:
            await ctx.send(embed=embed)
            embed = discord.Embed(title=str(word.id), description='{}:{}'.format(
                word.before, word.after), color=0x0000ff)
        else:
            embed.add_field(name=str(word.id), value='{}：{}'.format(
                word.before, word.after), inline=False)
    await ctx.send(embed=embed)
    await ctx.send("追加できてるか確認してな！")


@add_word.error
async def add_word_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("使い方ちゃうで？　`！へるぷ`みてな？", delete_after=15)


@bot.command(name="さくじょ")
async def del_word(ctx, num: int):
    if dict_del(num):
        words = dict_get()
        embed = discord.Embed(
            title="あおかぜぼっと速報", description="じしょいちらん", color=0x0000ff)
        embed.add_field(name='ばんごう', value='たんご：よみがな', inline=False)
        for i, word in enumerate(words, start=1):
            if i % 15 == 0:
                await ctx.send(embed=embed)
                embed = discord.Embed(title=str(word.id), description='{}:{}'.format(
                    word.before, word.after), color=0x0000ff)
            else:
                embed.add_field(name=str(word.id), value='{}:{}'.format(
                    word.before, word.after), inline=False)
        await ctx.send(embed=embed)
        await ctx.send('{}番を消しといたで'.format(num))
    else:
        await ctx.send('なんか消せんかったで', delete_after=15)


@del_word.error
async def del_word_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("使い方ちゃうで？　`！へるぷ`みてな？", delete_after=15)


@bot.command(name="じしょ")
async def dict_open(ctx):
    words = dict_get()
    embed = discord.Embed(
        title="あおかぜぼっと速報", description="あおかぜじしょいちらん", color=0x0000ff)
    embed.add_field(name='ばんごう', value='たんご：よみがな', inline=False)
    for i, word in enumerate(words, start=1):
        if i % 15 == 0:
            await ctx.send(embed=embed)
            embed = discord.Embed(title=str(word.id), description='{}:{}'.format(
                word.before, word.after), color=0x0000ff)
        else:
            embed.add_field(name=str(word.id), value='{}:{}'.format(
                word.before, word.after), inline=False)
    await ctx.send(embed=embed)


@bot.command(name="てんき", aliases=['天気の子'])
async def forecast(ctx, target: str):
    areas = ["釧路", "旭川", "札幌", "青森", "秋田", "仙台", "新潟", "金沢", "東京", "宇都宮",
             "長野", "名古屋", "大阪", "高松", "松江", "広島", "高知", "福岡", "鹿児島", "奄美", "那覇", "石垣"]
    if target in areas:
        url = 'https://www.jma.go.jp/bosai/forecast/data/forecast/010000.json'
        filename = 'tenki.json'
        request.urlretrieve(url, filename)
        with open('tenki.json', 'r', encoding="UTF-8") as f:
            data = json.load(f)
        await ctx.send(f"[ {target} ] の天気予報やで", delete_after=300)
        await ctx.send(embed=forecast_weathers(target, data), delete_after=300)
        await ctx.send(embed=forecast_winds(target, data), delete_after=300)
        await ctx.send(embed=forecast_pops(target, data), delete_after=300)
        await ctx.send(embed=forecast_temps(target, data), delete_after=300)
        await ctx.send(embed=forecast_overview(target, data), delete_after=300)
    else:
        await ctx.send("その地名には対応してないみたいや", delete_after=60)


@forecast.error
async def forecast_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        emb = discord.Embed(
            title="あおかぜ天気予報", description="つかいかた", color=0x0000ff)
        emb.add_field(name="！てんき　<地名>　で天気予報が見れるで　\n\n使える地名 :arrow_down:",
                      value="釧路 旭川 札幌 \n青森 秋田 仙台 \n新潟 金沢 東京 \n宇都宮 長野 名古屋 \n大阪 高松 松江 \n広島 高知 福岡 \n鹿児島 奄美 那覇 \n石垣")
        await ctx.send(embed=emb, delete_after=120)


class wordle:
    def __init__(self,mode):
        self.mode = mode
        if mode == "jp":
            words = open('wordlist.txt', 'r', encoding='UTF-8').read().split()
            self.table = [
 "あ","い","う","え","お"," ","か","き","く","け","こ"," ","さ","し","す","せ","そ","\n"
,"た","ち","つ","て","と"," ","な","に","ぬ","ね","の"," ","は","ひ","ふ","へ","ほ","\n"
,"ま","み","む","め","も"," ","や","　","ゆ","　","よ"," ","ら","り","る","れ","ろ","\n"
,"わ","　","を","　","ん"," ","　","　","　","　","　"," ","　","　","　","　","　","\n"
,"が","ぎ","ぐ","げ","ご"," ","ざ","じ","ず","ぜ","ぞ"," ","だ","ぢ","づ","で","ど","\n"
,"ば","び","ぶ","べ","ぼ"," ","ぱ","ぴ","ぷ","ぺ","ぽ"," ","　","　","　","　","　","\n"
,"ゃ","　","ゅ","　","ょ"," ","ぁ","ぃ","ぅ","ぇ","ぉ"," ","っ","　","ー","　","　"]
        elif mode == "pk":
            words = open('pokemon.txt', 'r', encoding='UTF-8').read().split()
            self.table = [
 "ア","イ","ウ","エ","オ"," ","カ","キ","ク","ケ","コ"," ","サ","シ","ス","セ","ソ","\n"
,"タ","チ","ツ","テ","ト"," ","ナ","ニ","ヌ","ネ","ノ"," ","ハ","ヒ","フ","ヘ","ホ","\n"
,"マ","ミ","ム","メ","モ"," ","ヤ","　","ユ","　","ヨ"," ","ラ","リ","ル","レ","ロ","\n"
,"ワ","　","ヲ","　","ン"," ","　","　","　","　","　"," ","　","　","　","　","　","\n"
,"ガ","ギ","グ","ゲ","ゴ"," ","ザ","ジ","ズ","ゼ","ゾ"," ","ダ","ヂ","ヅ","デ","ド","\n"
,"バ","ビ","ブ","ベ","ボ"," ","パ","ピ","プ","ペ","ポ"," ","　","　","　","　","　","\n"
,"ャ","　","ュ","　","ョ"," ","ァ","ィ","ゥ","ェ","ォ"," ","ッ","　","ー","　","　"]

        select = random.randint(0, len(words)-1)
        self.time = 0
        self.word = words[select]
        
        print(self.word)
    
    def input_word(self, input):
        self.correct = []
        self.exist = []
        
        if self.mode == "pk":
            input = wanakana.to_katakana(input)

        # 位置文字ともに正解か判定
        for i in range(5):
            if(self.word[i] == input[i]):
                self.correct.append(i)
        # 位置が正解か判定
        for w in self.word:
            for i in range(5):
                if(w == input[i]):
                    self.exist.append(i)
                    if input[i] in self.table:
                        self.table[self.table.index(input[i])] = f"__{input[i]}__ "

        for i in input:
            if not i in self.word:
                if i in self.table:
                    self.table[self.table.index(i)] = "　"

@bot.command(name="わーどる", aliases=["wordle"])
async def start(ctx):
    global Game
    Game = wordle("jp")
    view = View()

    for i in range(5):
        view.add_item(discord.ui.Button(
            disabled=True, label=' ', style=discord.ButtonStyle.gray))
    await ctx.reply('ひらがなモードでゲームを開始しました', view=view)

@bot.command(name="ぽけもん", aliases=["pokemon","ポケモン"])
async def pokemon(ctx):
    global Game
    Game = wordle("pk")
    view = View()

    for i in range(5):
        view.add_item(discord.ui.Button(
            disabled=True, label=' ', style=discord.ButtonStyle.gray))
    await ctx.reply('ポケモンモードでゲームを開始しました', view=view)


@bot.command(name="かいとう", aliases=["kaitou", "ans", "こたえ","解答","か"])
async def answer(ctx, ans: str):
    global Game
    view = View()
    gray = discord.ButtonStyle.gray  # gray:合っていない
    green = discord.ButtonStyle.green  # green:位置文字共に合っている
    red = discord.ButtonStyle.red  # red:文字は含まれるが位置が違う
    styles = [gray, gray, gray, gray, gray]

    if(len(ans) != 5):
        await ctx.reply('５文字で入力な！')
        return
    try:
        Game.input_word(ans)
    except:
        await ctx.reply('`！わーどる` をしてゲームを開始してな！')
        return
    # input_wordより得た結果をリストに格納
    for exist in Game.exist:
        styles[exist] = red
    for correct in Game.correct:
        styles[correct] = green
    # Viewにボタンを追加
    for i in range(5):
        view.add_item(discord.ui.Button(
            disabled=True, label=ans[i], style=styles[i]))
    # 結果表示
    nonword = "".join(Game.table)
    
    Game.time = Game.time+1
    
    await ctx.reply('--- 残ってる文字 ---\n'+str(nonword)+'\n--- 結果 '+str(Game.time)+'/6 ---', view=view)
    # クリアor失敗判定
    if(len(Game.correct) == 5):
        await ctx.reply('だいせいかい！！')
        del Game
        return
    if(Game.time == 6):
        await ctx.reply('ふせいかい こたえ:'+Game.word)
        del Game
        return


@bot.command(name="ちゅうだん", aliases=["きる"])
async def kill(ctx):
    global Game
    try:
        del Game
        await ctx.reply('ゲームを中断したで')
    except:
        await ctx.reply('ゲームやってないで')


@bot.event
async def on_message(message):
    global vc
    global tc
    global talk
    global calibration
    global target_language_code

    if message.author.bot:
        return

    if message.content.startswith("！"):
        await bot.process_commands(message)
        return

    if message.guild.id not in tc:
        return

    msg = remove_custom_emoji(message.clean_content)
    msg = remove_image(msg)
    msg = remove_url(msg)
    words = dict_get()
    for word in words:
        msg = msg.replace(word.before, word.after)
    print(msg)
    for attachment in message.attachments:
        if attachment.filename.endswith((".jpg", ".jpeg", ".gif", ".png", ".bmp")):
            msg += '、画像'
        else:
            msg += '、添付ファイル'
    if message.guild.voice_client:
        if vc[message.guild.id].is_connected:
            if message.channel.id == tc[message.guild.id]:
                while vc[message.guild.id].is_playing():
                    await asyncio.sleep(0.1)
                play_voice(msg, message.guild.voice_client)
                await asyncio.sleep(0.5)
    if talk:
        files = {'apikey': (None, TALK_API), 'query': (None, msg), }
        r = requests.post(TALK_API_URL, files=files)
        response = r.json()
        print(response)
        if response["status"] == 0:
            reply = response["results"][0]["reply"]
            await message.channel.send(reply)
            if message.guild.voice_client:
                play_voice(reply, message.guild.voice_client)
                await asyncio.sleep(0.5)
        else:
            await message.channel.send("( ˙꒳​˙  )???")
    if calibration:
        response = post(msg)
        await message.channel.send(response)
    if translation:
        if message.channel.id == 961144686729388042:

            zatudan = bot.get_channel(512622643187548163)
            
            translate_response = any2jp(msg)
            for result in translate_response.translations:
                print("Translated text: {}".format(result.translated_text))
                await zatudan.send(result.translated_text)
        
        if message.channel.id == tc[message.guild.id]:
            translate_ch = bot.get_channel(961144686729388042)

            translate_response2any = jp2any(msg,target_language_code[target_language_num])
            for result in translate_response2any.translations:
                print("Translated text: {}".format(result.translated_text))
                await translate_ch.send(result.translated_text)



@bot.event
async def on_member_join(member):
    print(member.name)
    guild = member.guild  # サーバー
    sysch = guild.system_channel  # 参加メッセージを表示するチャンネル
    category = bot.get_channel(659906186413342752)
    new_channel = await category.create_text_channel(member.name)
    await new_channel.send(member.mention+"ここが個人の部屋になります！\n\n3勝ミッションを取るまで戦略立てるので確認お願いします！\n\nまた、この部屋はメアの報告や、装備相談などに使ってください！\n\n他の人の部屋は好きに見てくれて大丈夫です！\n同じジョブの人はこの部屋に書き込むことができます！\nメアと装備のスクショをお願いします")
    # if sysch: # チャンネルが設定されてなかったら何もしない
    #     welcome_emb = discord.Embed(title="あおかぜぼっと速報", description=f'{member.mention} いらっしゃい！\nわいはあおかぜぼっとや！\n蒼風サーバーについていろいろ教えるで！', color=0x0000ff)
    #     welcome_emb.add_field(name=new_channel.id,value="あなたのための部屋やで！",inline=False)
    #     welcome_emb.set_footer(text=get_now().strftime(dayformat))
    #     await sysch.send(embed=welcome_emb)


@bot.event
async def on_voice_state_update(member, before, after):
    global botti
    global vc
    global tc
    global entry_and_exit
    if entry_and_exit:
        zatudan = bot.get_channel(512622643187548163)
        if before.channel is None:
            if member.guild.voice_client:
                if member.guild.voice_client.channel is after.channel:
                    text = f'{member.display_name} が {after.channel.name} に参加しました。'
                    while member.guild.voice_client.is_playing():
                        await asyncio.sleep(0.5)
                    play_voice(text, member.guild.voice_client)
                    await zatudan.send(text, delete_after=15)

        elif after.channel is None:
            if member.guild.voice_client:
                if member.guild.voice_client.channel is before.channel:
                    text = f'{member.display_name} が {before.channel.name} から退出しました。'
                    while member.guild.voice_client.is_playing():
                        await asyncio.sleep(0.5)
                    play_voice(text, member.guild.voice_client)
                    await zatudan.send(text, delete_after=15)

    if botti:
        if after.channel is None:
            if member.guild.voice_client.channel is before.channel:
                if len(member.guild.voice_client.channel.members) == 1:
                    await asyncio.sleep(0.5)
                    await member.guild.voice_client.disconnect()
                    if vc[member.guild.id].is_connected:
                        print("read_stop!!")
                        vc[member.guild.id].stop()
                        await vc[member.guild.id].disconnect()
                        await tc[member.guild.id].send(embed=make_emb(bot.latency * 1000, ":mute: 読み上げ終了", member.author.display_name, member.author.display_avatar))
                        await tc[member.guild.id].send("ぼっちはいやじゃあ！")


@tasks.loop(seconds=1)
async def loop():
    global colo
    aokz_radio = bot.get_channel(512622643644596230)
    zatudan = bot.get_channel(904753777108721694)
    if colo:
        global vc
        global tc
        global order
        now = get_now()
        base = datetime.datetime(
            now.year, now.month, now.day, 22, 57, 00).strftime(dayformat)
        start = datetime.datetime(
            now.year, now.month, now.day, 22, 59, 00).strftime(dayformat)
        end = datetime.datetime(
            now.year, now.month, now.day, 23, 20, 00).strftime(dayformat)
        if now.strftime(dayformat) == base:
            if not vc[aokz_radio.guild.id].is_connected:
                vc[aokz_radio.guild.id] = await aokz_radio.connect()
                await zatudan.send(random.choice(inmsg))
            ws = connect_gspread()
            i = 4
            await zatudan.send("～～～～　今日のメニュー　～～～～")
            while ws.cell(i, 3).value != '・END':
                order.append([ws.cell(i, 2).value, ws.cell(
                    i, 3).value, ws.cell(i, 4).value, ws.cell(i, 10).value])
                await zatudan.send(order[i-4][1]+"　"+order[i-4][2])
                i = i+1

        if now.strftime(dayformat) == start:
            while vc[aokz_radio.guild.id].is_playing():
                await asyncio.sleep(0.1)
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("hora.mp3"), volume=0.25)
            vc[aokz_radio.guild.id].play(source)
            while vc[aokz_radio.guild.id].is_playing():
                await asyncio.sleep(0.1)
            play_voice("あおかぜぼっと、コロシアムモードに移行します", vc[aokz_radio.guild.id])
            await asyncio.sleep(55)
            for text in order:
                timer = text[0].split(':')
                msg = timer[1]+"分"+timer[2]+"秒"+" に " + \
                    text[2]+" さん "+text[1].strip("・")
                await zatudan.send(msg, delete_after=60)
                while vc[aokz_radio.guild.id].is_playing():
                    await asyncio.sleep(0.1)
                play_voice(str(msg), vc[aokz_radio.guild.id])
                await asyncio.sleep(int(text[3]))
                if not colo:
                    break

        if now.strftime(dayformat) == end:
            while vc[aokz_radio.guild.id].is_playing():
                await asyncio.sleep(0.1)
            play_voice("あおかぜぼっと、コロシアムモードを終了します", vc[aokz_radio.guild.id])
            await asyncio.sleep(1)
            os.remove("voice.webm")


@loop.before_loop
async def before_loop():
    print('waiting...')
    await bot.wait_until_ready()


def text_to_ssml(text):
    escaped_lines = html.escape(text)
    ssml = "{}".format(
        escaped_lines.replace("\n", "  ")
    )
    return ssml


def ssml_to_speech(ssml, file, language_code, gender):
    ttsclient = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=ssml)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, name=speaker[who], ssml_gender=gender
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.OGG_OPUS,
        speaking_rate=1.2
    )
    response = ttsclient.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(file, "wb") as out:
        out.write(response.audio_content)
        print("Audio content written to file " + file)
    return file


def ibm_speech(ssml, file):
    res = ibm_tts.synthesize(
        ssml, accept="audio/ogg;codecs=opus", voice="ja-JP_EmiV3Voice").get_result()
    with open(file, 'wb') as out:
        out.write(res.content)
        print("Audio content written to file " + file)
    return file


def play_voice(text, voice):
    words = dict_get()
    for word in words:
        text = text.replace(word.before, word.after)
    ssml = text_to_ssml(text)
    if who >= 5:
        #file = generate_wav(ssml, who2id(who), "voice.webm")
        file = web_voicevox(ssml, who2id(who))
    elif who == 4:
        file = ibm_speech(ssml, "voice.webm")
    else:
        file = ssml_to_speech(ssml, "voice.webm", "ja-JP",
                              texttospeech.SsmlVoiceGender.NEUTRAL)
    voice.play(discord.FFmpegOpusAudio(file))


def generate_wav(text, speaker=1, file='voice.webm'):
    params = (
        ('text', text),
        ('speaker', speaker)
    )
    response1 = requests.post(
        f'http://{VOICEVOX_HOST}:{VOICEVOX_PORT}/audio_query',
        params=params,
        timeout=(10.0, 20.0)
    )

    headers = {'Content-Type': 'application/json', }
    response2 = requests.post(
        f'http://{VOICEVOX_HOST}:{VOICEVOX_PORT}/synthesis',
        headers=headers,
        params=params,
        data=json.dumps(response1.json()),
        timeout=(10.0, 20.0)
    )

    with open(file, 'wb') as wf:
        wf.write(response2.content)

    return file


def web_voicevox(text, speaker=1):
    return f'https://api.su-shiki.com/v2/voicevox/audio/?text={text}&key={VOICEVOX_API_KEY}&speaker={speaker}'


def who2id(who):
    if who == 5:
        return 0
    elif who == 6:
        return 2
    elif who == 7:
        return 4
    elif who == 8:
        return 6
    elif who == 9:
        return 1
    elif who == 10:
        return 3
    elif who == 11:
        return 5
    elif who == 12:
        return 7
    elif who == 13:
        return 8
    elif who == 14:
        return 9
    elif who == 15:
        return 10


def any2jp(text):
    project_id="aokazebot-texttospeach"
    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    # Translate text from English to French
    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "target_language_code": "ja",
        }
    )

    return response


def jp2any(text,target_language_code="en"):
    project_id="aokazebot-texttospeach"
    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    # Translate text from English to French
    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "target_language_code": target_language_code,
        }
    )

    return response


def random_color():
    return discord.Color.from_rgb(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))


def get_now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))


def remove_custom_emoji(text):
    pattern1 = r'<:'    # カスタム絵文字のパターン
    pattern2 = r':[0-9]+>'
    text = re.sub(pattern1, "", text)
    return re.sub(pattern2, "", text)


def remove_url(text):
    pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    return re.sub(pattern, 'URL', text)   # 置換処理


def remove_image(text):
    pattern = r'.*(\.jpg|\.jpeg|\.gif|\.png|\.bmp)'
    return re.sub(pattern, '画像', text)


def connect_gspread():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SPREADSHEET_JSON, scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1
    return worksheet


def loto(num):
    if num == 0:
        return '\n晩鐘は汝の名を指し示した・・・\n\n\n\t~~♰死告天使(ｱｽﾞﾗｲｰﾙ)♰~~\n\n\n'
    elif num == 1:
        return '\n＿人人人人人人人人人人人人人人人＿\n    あなたがジャンプマスターです\nー^Y^Y^Y^Y^Y^Y^Y^Y^Y^Y^Y^Y^Y^ー\n\n　　　　　\      □ 出撃       /\n　　　　　　\  ○ 譲渡  /'
    elif num in range(2, 49):
        return random.choice(inmsg)
    elif num in range(50, 100):
        return random.choice(outmsg)


def make_emb(latency, des, author, icon):
    if round(latency) <= 50:
        embed = discord.Embed(
            title="あおかぜぼっと速報", description=des, color=0x44ff44)
        embed.add_field(name=":satellite: 接続状態", value="絶好調")
    elif round(latency) <= 100:
        embed = discord.Embed(
            title="あおかぜぼっと速報", description=des, color=0xffd000)
        embed.add_field(name=":satellite: 接続状態", value="まあまあ")
    elif round(latency) <= 200:
        embed = discord.Embed(
            title="あおかぜぼっと速報", description=des, color=0xff6600)
        embed.add_field(name=":satellite: 接続状態", value="つらたん")
    else:
        embed = discord.Embed(
            title="あおかぜぼっと速報", description=des, color=0x990000)
        embed.add_field(name=":satellite: 接続状態",
                        value="もうマジ無理\n<@!614978622104666190>を呼んでな")
    embed.set_author(name=author, icon_url=icon)
    embed.add_field(name=":hourglass: 遅延",
                    value=f"{round(bot.latency *1000)} ms")
    embed.add_field(name=":speaking_head: 担当", value=speaker[who])
    embed.set_footer(text=get_now().strftime(dayformat))
    return embed


class Setting:
    def __init__(self, dif_rate, rows, clear_range, response):
        self.dif_rate = dif_rate
        self.rows = rows
        self.clear_range = clear_range
        self.response = '[ LEVEL {} ]'.format(response)


def minesweeper(level):
    response_string = ''
    bomb_count = 0
    if level == "1" or level == "１":
        dif = Setting(0.1, 8, [3, 4], 1)
    elif level == "2" or level == "２":
        dif = Setting(0.15, 10, [3, 5], 2)
    elif level == "3" or level == "３":
        dif = Setting(0.2, 10, [4, 7], 3)
    elif level == "4" or level == "４":
        dif = Setting(0.25, 10, [4, 6], 4)
    elif level == "5" or level == "５":
        dif = Setting(0.3, 10, [4, 6], 5)
    elif level == "6" or level == "６":
        dif = Setting(0.35, 10, [4, 6], 6)
    elif level == "7" or level == "７":
        dif = Setting(0.4, 10, [4, 6], 7)
    elif level == "8" or level == "８":
        dif = Setting(0.45, 10, [4, 6], 8)
    elif level == "9" or level == "９":
        dif = Setting(0.5, 10, [4, 6], 9)
    elif level == "10" or level == "１０":
        dif = Setting(0.55, 10, [4, 6], 10)
    elif level == "999" or level == "９９９":
        dif = Setting(0.9, 8, [4, 6], 999)
    else:
        return "そんなレベルないで？"
    response_string += dif.response+'\n'
    # 盤面の初期化、および爆弾設置(100)
    stage = [[100 if random.random() < dif.dif_rate else 0 for x in range(dif.rows+1)]
             for y in range(dif.rows+1)]

    # 爆弾を探索し、周辺マスをカウントアップ
    for x in range(dif.rows):
        for y in range(dif.rows):
            try:
                if stage[x][y] >= 100:
                    stage[x-1][y-1] += 1
                    stage[x][y-1] += 1
                    stage[x+1][y-1] += 1

                    stage[x-1][y] += 1
                    stage[x+1][y] += 1

                    stage[x-1][y+1] += 1
                    stage[x][y+1] += 1
                    stage[x+1][y+1] += 1
            except (IndexError) as e:
                pass

    # 伏せ字への変換
    for x in range(dif.rows):
        for y in range(dif.rows):
            if dif.clear_range[0] <= x <= dif.clear_range[1] and dif.clear_range[0] <= y <= dif.clear_range[1]:
                if stage[x][y] == 0:
                    stage[x][y] = ":zero:"
                elif stage[x][y] == 1:
                    stage[x][y] = ":one:"
                elif stage[x][y] == 2:
                    stage[x][y] = ":two:"
                elif stage[x][y] == 3:
                    stage[x][y] = ":three:"
                elif stage[x][y] == 4:
                    stage[x][y] = ":four:"
                elif stage[x][y] == 5:
                    stage[x][y] = ":five:"
                elif stage[x][y] == 6:
                    stage[x][y] = ":six:"
                elif stage[x][y] == 7:
                    stage[x][y] = ":seven:"
                elif stage[x][y] == 8:
                    stage[x][y] = ":eight:"
                elif stage[x][y] >= 100:
                    stage[x][y] = "||:bomb:||"
                    bomb_count += 1
            else:
                if stage[x][y] >= 100:
                    stage[x][y] = "||:bomb:||"
                    bomb_count += 1
                elif stage[x][y] == 0:
                    stage[x][y] = "||:zero:||"
                elif stage[x][y] == 1:
                    stage[x][y] = "||:one:||"
                elif stage[x][y] == 2:
                    stage[x][y] = "||:two:||"
                elif stage[x][y] == 3:
                    stage[x][y] = "||:three:||"
                elif stage[x][y] == 4:
                    stage[x][y] = "||:four:||"
                elif stage[x][y] == 5:
                    stage[x][y] = "||:five:||"
                elif stage[x][y] == 6:
                    stage[x][y] = "||:six:||"
                elif stage[x][y] == 7:
                    stage[x][y] = "||:seven:||"
                elif stage[x][y] == 8:
                    stage[x][y] = "||:eight:||"
                elif 9 <= stage[x][y] < 100:
                    return minesweeper(level)
            response_string += str(stage[x][y])
        response_string += "\n"
    return response_string + "💣ばくだん{}こ💣".format(bomb_count)


def post(query):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Yahoo AppID: {}".format(YAHOO_API_KEY),
    }
    param_dic = {
        "id": "1234-1",
        "jsonrpc": "2.0",
        "method": "jlp.kouseiservice.kousei",
        "params": {
            "q": query
        }
    }
    params = json.dumps(param_dic).encode()
    req = request.Request(YAHOO_API_URL, params, headers)
    with request.urlopen(req) as res:
        body = res.read()
    return body.decode()


def forecast_weathers(target, data):
    for area in data:
        name = area['name']

        if name == target:
            time = area['srf']["reportDatetime"]
            emb = discord.Embed(
                title="あおかぜ天気予報", description=f"{time[:10]} {time[11:16]} 更新", color=0x0000ff, url="https://www.jma.go.jp/bosai/forecast/")
            for ts in area['srf']['timeSeries']:
                times = [n for n in ts['timeDefines']]
                if 'weathers' in ts['areas']:
                    text = ""
                    for i, v in enumerate(ts['areas']['weathers']):
                        text += f"{times[i][:10]} : {v}\n"
                    emb.add_field(name=f"[ {name} ] の天気",
                                  value=text, inline=False)
    return emb


def forecast_winds(target, data):
    for area in data:
        name = area['name']

        if name == target:
            time = area['srf']["reportDatetime"]
            emb = discord.Embed(
                title="あおかぜ天気予報", description=f"{time[:10]} {time[11:16]} 更新", color=0x0000ff, url="https://www.jma.go.jp/bosai/forecast/")
            for ts in area['srf']['timeSeries']:
                times = [n for n in ts['timeDefines']]
                if 'winds' in ts['areas']:
                    text = ""
                    for i, v in enumerate(ts['areas']['winds']):
                        text += f"{times[i][:10]} : {v}\n"
                    emb.add_field(name=f"[ {name} ] の風速",
                                  value=text, inline=False)
    return emb


def forecast_pops(target, data):
    for area in data:
        name = area['name']

        if name == target:
            time = area['srf']["reportDatetime"]
            emb = discord.Embed(
                title="あおかぜ天気予報", description=f"{time[:10]} {time[11:16]} 更新", color=0x0000ff, url="https://www.jma.go.jp/bosai/forecast/")
            for ts in area['srf']['timeSeries']:
                times = [n for n in ts['timeDefines']]
                if 'pops' in ts['areas']:
                    text = ""
                    for i, v in enumerate(ts['areas']['pops']):
                        text += f"{times[i][:10]}  {times[i][11:16]} : {v}%\n"
                    emb.add_field(name=f"[ {name} ] の降水確率",
                                  value=text, inline=False)
    return emb


def forecast_temps(target, data):
    for area in data:
        name = area['name']

        if name == target:
            time = area['srf']["reportDatetime"]
            emb = discord.Embed(
                title="あおかぜ天気予報", description=f"{time[:10]} {time[11:16]} 更新", color=0x0000ff, url="https://www.jma.go.jp/bosai/forecast/")
            for ts in area['srf']['timeSeries']:
                times = [n for n in ts['timeDefines']]
                if 'temps' in ts['areas']:
                    text = f"{times[0][:10]} : {ts['areas']['temps'][0]}/{ts['areas']['temps'][1]}\n"
                    if len(ts['areas']['temps']) > 2:
                        text = f"{times[0][:10]} : {ts['areas']['temps'][2]}/{ts['areas']['temps'][3]}"
                    emb.add_field(
                        name=f"[ {name} ] の気温　最低/最高(℃)", value=text, inline=False)
    return emb


def forecast_overview(target, data):
    for area in data:
        name = area['name']

        if name == target:
            time = area['srf']["reportDatetime"]
            code = area["officeCode"]
            url = f'https://www.jma.go.jp/bosai/forecast/data/overview_forecast/{code}.json'
            filename = f'{code}.json'
            request.urlretrieve(url, filename)
            with open(filename, 'r', encoding="UTF-8") as f:
                d = json.load(f)
            emb = discord.Embed(title="あおかぜ天気予報", description=d["reportDatetime"][:10]+" "+d["reportDatetime"]
                                [11:16]+" 更新", color=0x0000ff, url="https://www.jma.go.jp/bosai/forecast/")
            emb.add_field(name=f"[ {name} ] の天気予報",
                          value=d["headlineText"]+d["text"], inline=False)
    return emb




# DB
Base = declarative_base()


class dict(Base):
    __tablename__ = "dict"  # テーブル名を指定
    id = Column(Integer, primary_key=True, autoincrement=True)
    before = Column(String(255))
    after = Column(String(255))


Base.metadata.create_all(engine)

SessionClass = orm.sessionmaker(bind=engine)  # セッションを作るクラスを作成
session = SessionClass()


def dict_add(word, read):
    dictionary = session.query(dict).filter_by(before=word).one_or_none()
    if isinstance(dictionary, type(None)):
        dictionary = dict(before=word, after=read)
        session.add(dictionary)
        session.commit()
    else:
        set_dict(read, dictionary)


def set_dict(read, dictionary):
    dictionary.read = read
    session.commit()


def dict_del(del_id):
    found_dict = session.query(dict).filter_by(id=del_id).one_or_none()
    if isinstance(found_dict, type(None)):
        return None
    else:
        session.delete(found_dict)
        session.commit()
        return True


def dict_get():
    dictionary = session.query(dict)
    session.commit()
    return dictionary


loop.start()
bot.run(TOKEN)
