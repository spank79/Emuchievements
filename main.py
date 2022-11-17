import hashlib
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict

sys.path.append(os.path.dirname(__file__))
from retroachievements import RetroAchievements, Game
from settings import SettingsManager

logging.basicConfig(
	filename="/tmp/emuchievements.log",
	format='[Emuchievements] %(asctime)s %(levelname)s %(message)s',
	filemode='w+',
	force=True
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # can be changed to logging.DEBUG for debugging issues


class Plugin:
	settings: SettingsManager
	username: str
	api_key: str
	hidden: bool = False

	async def Hash(self, path: str) -> str:
		return subprocess.run([os.path.dirname(__file__) + '/bin/Emuchievements', path], stdout=subprocess.PIPE).stdout.decode('utf-8')

	async def Login(self, username: str, api_key: str):
		Plugin.username = username
		Plugin.api_key = api_key
		await Plugin.commit(self)

	async def isLogin(self) -> bool:
		return (Plugin.username is not None) and (Plugin.api_key is not None)

	async def Hidden(self, hidden: bool):
		Plugin.hidden = hidden
		await Plugin.commit(self)

	async def isHidden(self) -> bool:
		return Plugin.hidden

	async def GetUserRecentlyPlayedGames(self, count: int | None) -> List[Game]:
		client = RetroAchievements(Plugin.username, Plugin.api_key)
		return await client.GetUserRecentlyPlayedGames(Plugin.username, count)

	async def GetGameInfoAndUserProgress(self, game_id: int) -> Game:
		client = RetroAchievements(Plugin.username, Plugin.api_key)
		return await client.GetGameInfoAndUserProgress(Plugin.username, game_id)

	# Asyncio-compatible long-running code, executed in a task when the plugin is loaded
	async def _main(self):
		Plugin.settings = SettingsManager("emuchievements")
		await Plugin.read(self)

	async def read(self):
		Plugin.settings.read()
		Plugin.username = await Plugin.getSetting(self, "username", None)
		Plugin.api_key = await Plugin.getSetting(self, "api_key", None)
		Plugin.hidden = await Plugin.getSetting(self, "hidden", False)
		await Plugin.commit(self)

	async def commit(self):
		await Plugin.setSetting(self, "username", Plugin.username)
		await Plugin.setSetting(self, "api_key", Plugin.api_key)
		await Plugin.setSetting(self, "hidden", Plugin.hidden)
		Plugin.settings.commit()

	async def getSetting(self, key, default):
		return Plugin.settings.getSetting(key, default)

	async def setSetting(self, key, value):
		Plugin.settings.setSetting(key, value)
