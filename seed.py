from app import db
from models import User, Mod, SubImages, Game

db.drop_all()
db.create_all()

u1 = User(
    username='Admin',
    email='test@test.com',
    password='gaopineroighnarohgnhadfhogiaer0i04',
)

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

m1 = Mod(mod_name='Test1', game_id=1, upload_user_id=1, description="This is a test",
         requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')
m2 = Mod(mod_name='Test2', game_id=1, upload_user_id=1, description="This is a test",
         requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m3 = Mod(mod_name='Test3', game_id=1, upload_user_id=1, description="This is a test",
         requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m4 = Mod(mod_name='Test4', game_id=1, upload_user_id=1, description="This is a test",
         requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m5 = Mod(mod_name='Test5', game_id=1, upload_user_id=1, description="This is a test",
         requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m6 = Mod(mod_name='Test6', game_id=1, upload_user_id=1, description="This is a test",
         requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m7 = Mod(mod_name='Test7', game_id=1, upload_user_id=1, description="This is a test",
         requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m8 = Mod(mod_name='Test8', game_id=1, upload_user_id=1, description="This is a test",
         requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m9 = Mod(mod_name='Test9', game_id=1, upload_user_id=1, description="This is a test",
         requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m10 = Mod(mod_name='Test10', game_id=1, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m11 = Mod(mod_name='Test11', game_id=2, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')
m12 = Mod(mod_name='Test12', game_id=2, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m13 = Mod(mod_name='Test13', game_id=2, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m14 = Mod(mod_name='Test14', game_id=2, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m15 = Mod(mod_name='Test15', game_id=2, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m16 = Mod(mod_name='Test16', game_id=2, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m17 = Mod(mod_name='Test17', game_id=2, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m18 = Mod(mod_name='Test18', game_id=2, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m19 = Mod(mod_name='Test19', game_id=2, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')

m20 = Mod(mod_name='Test20', game_id=2, upload_user_id=1, description="This is a test",
          requirements='of the overall features', installation='of this mod app', file_id='Y_tho_Japanese.7z')


db.session.add_all([u1, g1, g2, m1, m2, m3, m4, m5, m6, m7, m8,
                    m9, m10, m11, m12, m13, m14, m15, m16, m17, m18, m19, m20])
db.session.commit()
