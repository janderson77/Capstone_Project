from app import db
from models import User, Mod, SubImages, Game

db.drop_all()
db.create_all()

g1 = Game(
    game_title='Mordrim',
    game_developer='Bethrest',
    game_genre='RPG',
    release_year=2011,
    game_image="static/images/mordrim/mordrim",
    description="The Ancient Tomes V: Mordrim is an action role-playing game, playable from either a first or third-person perspective. The player may freely roam over the land of Mordrim which is an open world environment consisting of wilderness expanses, dungeons, caves, cities, towns, fortresses, and villages."
)

g2 = Game(
    game_title='Aftermath 4',
    game_developer='Bethrest',
    game_genre='RPG',
    release_year=2015,
    game_image="static/images/aftermath_4/aftermath_4",
    description="Aftermath 4 is an action role-playing game developed by Bethrest Game Studios and published by Bethrest Softworks. The player explores the game's dilapidated world, completes various quests, helps out factions, and acquires experience points to level up and increase the abilities of their character."
)

db.session.add_all([g1, g2])
db.session.commit()
