"""

Surveybot: The anomaly-tracking discord bot

This bot is for a Roblox game called Starscape, and it keeps track of anomalies and aberrations in the game.

Creator: @Game_Collabs (Epicotch🍍#3765)

"""

import sqlite3, time, os
from disnake.ext import commands
import disnake as dis
from spellchecker import SpellChecker
os.system("clear")

database = sqlite3.connect('surveybot.db')
db_cursor = database.cursor()
prefixes = {"WH": "Wormhole", "AT": "Asteroid deposit", "AN": "Narcor deposit", "AL": "Large asteroid deposit", "AN": "Narcor deposit", "VX": "Vexnium deposit", "FO": "Frontier outpost", "DH": "Drone hangar", "CM": "Comet", "BF": "Battlefield", "SP": "Spice platform", "MT": "Monument", "X": "Structure", "R": "Ring deposit", "S-WH": "Stable wormhole", "Factory": "Drone Factory", "Den": "Pirate Den", "Fleet": "Drone Fleet"}

anomaly_abbr = commands.option_enum({"AT (Asteroid Deposit)": "AT", "AL (Large Deposit)": "AL", "AA (Axnit Deposit)": "AA", "AN (Narcor Deposit)": "AN", "VX (Vexnium Deposit)": "VX", "WH (Transient Wormhole)": "WH", "WH (Stable Wormhole)": "S-WH", "FO (Frontier Outpost)": "FO", "MT (Monument)": "MT", "DH (Drone Hangar)": "DH", "CM (Comet)": "CM", "SP (Spice Platofrm)": "SP", "BF (Battlefield)": "BF"})
planetary_abbr = commands.option_enum({"X (Structure)": "X", "R (Deposit)": "R", "Drone Factory": "Factory", "Pirate Den": "Den", "Drone Fleet": "Fleet"})

d = SpellChecker()

bot = commands.Bot(
    sync_commands_debug=True,
    test_guilds = [826924911767453697, 977412042782826598],
    prefix = commands.when_mentioned
)

async def update(serv = ''):
    """
    Clears outdated anomalies from the database.
    """
    db_cursor.execute(f"DELETE FROM anomalies{serv} WHERE time < {float((time.time() - 172800))} AND name != 'WH-S'")
    db_cursor.execute(f"DELETE FROM anomalies{serv} WHERE time < {float((time.time() - 604800))}")
    db_cursor.execute(f"DELETE FROM aberrations{serv} WHERE time < {float((time.time() - 172800))}")
    database.commit()

@bot.slash_command(description="Debug command to create SQL tables. WARNING: WILL DELETE ALL DATA")
@commands.default_member_permissions(administrator=True)
async def setup(inter):
    db_cursor.execute(f'''CREATE TABLE anomalies{inter.guild_id} (name text, number integer, system text, notes text, time real)''')
    db_cursor.execute(f'''CREATE TABLE aberrations{inter.guild_id} (name text, number integer, system text, planet integer, notes text, time real)''')
    db_cursor.execute(f"CREATE TABLE leaderboard{inter.guild_id} (userid int, name text, score int)")
    database.commit()
    await inter.response.send_message("Setup complete! Use /refresh for future table clears.")

@bot.slash_command(description="Debug command to create SQL tables. WARNING: WILL DELETE ALL DATA")
@commands.default_member_permissions(administrator=True)
async def refresh(inter):
    """
    Deletes all information from the tables and creates new ones.
    """
    db_cursor.execute("DROP TABLE anomalies" + str(inter.guild_id))
    db_cursor.execute("DROP TABLE aberrations" + str(inter.guild_id))
    db_cursor.execute(f'''CREATE TABLE anomalies{inter.guild_id} (name text, number integer, system text, notes text, time real)''')
    db_cursor.execute(f'''CREATE TABLE aberrations{inter.guild_id} (name text, number integer, system text, planet integer, notes text, time real)''')
    database.commit()

    await inter.response.send_message('Tables refreshed!')
@bot.slash_command(description="Debug command to create SQL tables. WARNING: WILL DELETE ALL DATA")
@commands.default_member_permissions(administrator=True)
async def refreshleaderboard(inter):
    """
    Deletes the leaderboard and creates a new one.
    """
    db_cursor.execute("DROP TABLE leaderboard" + str(inter.guild_id))
    db_cursor.execute(f"CREATE TABLE leaderboard{inter.guild_id} (userid int, name text, score int)")
    database.commit()
    await inter.response.send_message("Done!")

@bot.slash_command(description="Get the discoveries leaderboard!")
async def leaderboard(inter, scope: str = ''):
    """
    Command to show leaderboards.
    """
    gid = ""
    if scope.strip().upper() != "GLOBAL":
        gid += str(inter.guild_id)
    info = db_cursor.execute(f"SELECT * FROM leaderboard{gid} ORDER BY score ASC").fetchmany(10)
    print(info)
    outputstring = ""
    #iter = 0
    for i in info:
        outputstring += i[1] + ": " + str(i[2]) + "\n"
        #iter += 1
        #if iter > 10: break
    emb = dis.Embed(color = dis.Color.green(), title = "Discoveries leaderboard", description = outputstring)
    await inter.response.send_message(embed = emb)

@bot.slash_command()
async def register(inter):
    """
    Parent command to register anomalies.
    """
    if len(db_cursor.execute("SELECT * FROM leaderboard WHERE userid=:userid", {"userid": inter.author.id}).fetchall()) != 0:
        print("User found, updating score...")
        db_cursor.execute("UPDATE leaderboard SET score = score + 1 WHERE userid=:userid", {"userid": inter.author.id})
        database.commit()
    else:
        print("User not found, making entry...")
        db_cursor.execute("INSERT INTO leaderboard VALUES (?, ?, ?)", (inter.author.id, inter.author.display_name, 1))
        database.commit()
    if len(db_cursor.execute(f"SELECT * FROM leaderboard{str(inter.guild_id)} WHERE userid=:userid", {"userid": inter.author.id}).fetchall()) != 0:
        print("User found, updating score...")
        db_cursor.execute(f"UPDATE leaderboard{str(inter.guild_id)} SET score = score + 1 WHERE userid=:userid", {"userid": inter.author.id})
        database.commit()
    else:
        print("User not found, making entry...")
        db_cursor.execute(f"INSERT INTO leaderboard{str(inter.guild_id)} VALUES (?, ?, ?)", (inter.author.id, inter.author.display_name, 1))
        database.commit()

@register.sub_command(description="Register an anomaly in the bot's database")
async def anomaly(inter, type: anomaly_abbr, number: int, system: str, notes: str = '', scope: str = ''):
    """
    Subcommand which inserts anomalies into database
    """
    gid = ''
    if scope.strip().upper() != "GLOBAL":
        gid += str(inter.guild_id)
    db_cursor.execute(f"INSERT INTO anomalies{gid} VALUES (?, ?, ?, ?, ?)", [type.upper(), number, system.upper(), notes, time.time()])
    if type == "WH" or type == "S-WH":
        recievingName = ""
        recievingName = " ".join(list(d.unknown(notes.split(" "))))
        words = ["THE CITADEL", "AEGIS", "TRIAGE", "SHIELD", "BASTION", "GUARD", "SIZE"]
        for i in notes.upper().split(" "):
            if i in words:
                recievingName += system.upper()
        print("Stripped " + notes + " into " + recievingName)
        db_cursor.execute(f"INSERT INTO anomalies{gid} VALUES (?, ?, ?, ?, ?)", [type.upper(), number, recievingName.strip().upper(), "Leads to " + system.capitalize(), time.time()])
    database.commit()
    await inter.response.send_message('Anomaly registered!')

@register.sub_command(description="Register an aberration/factory/den/fleet in the bot's database")
async def planetary(inter, type: planetary_abbr, number: int, system: str, planet: int, notes: str = '', scope: str = ''):
    """
    Subcommand which inserts aberrations into database.
    """
    gid = ''
    if scope.strip().upper() != "GLOBAL":
        gid += str(inter.guild_id)
    db_cursor.execute(f"INSERT INTO aberrations{gid} VALUES (?, ?, ?, ?, ?, ?)", [type.upper(), number, system.upper(), planet, notes, time.time()])
    database.commit()
    await inter.response.send_message('Planetary registered!')

@bot.slash_command(description="Get a list of anomalies")
async def anomalies(inter, type: str = None, system: str = None, scope: str = ''):
    """
    Command to display currently stored anomalies
    """
    gid = ''
    if scope.strip().upper() != "GLOBAL":
        gid += str(inter.guild_id)
    await update(gid)
    titletext = "Anomalies"
    if type != None:
        titletext = titletext.lower()
        titletext += prefixes[type] + " "
    if system != None:
        titletext += " in " + system.capitalize()
    inst = f"SELECT * FROM anomalies{gid}"
    sys = None
    if type != None:
        inst += " WHERE name=:type"
    if type != None and system != None:
        inst += " AND"
    if system != None:
        if type == None:
            inst += " WHERE"
        inst += " system=:system"
        sys = system.upper()
        
    emb = dis.Embed(colour=dis.Color.dark_blue(), title=titletext, description="Currently tracked anomalies:")
    anoms = db_cursor.execute(inst, {"type": type, "system": sys}).fetchall()
    print(anoms)
    for anom in anoms:
        emb.add_field(str(anom[0]) + "-" + str(anom[1]), "**System:** " + str(anom[2]).capitalize() + "\n**Notes:** " + str(anom[3]) + "\n**Discovered on:** <t:" + str(int(anom[4])) + "> (<t:" + str(int(anom[4])) + ":R>)")
    await inter.response.send_message(embed=emb)

@bot.slash_command(description="Get a list of planetaries", aliases=["aberrations"])
async def planetaries(inter, type: str = None, system: str = None, scope: str = ''):
    """
    Command to display currently stored aberrations
    """
    gid = ''
    if scope.strip().upper() != "GLOBAL":
        gid += str(inter.guild_id)
    await update(gid)
    titletext = "Planetaries"
    if type != None:
        titletext = titletext.lower()
        titletext += prefixes[type] + " "
    if system != None:
        titletext += " in " + system.capitalize()
    inst = "SELECT * FROM aberrations" + gid
    sys = None
    if type != None:
        inst += " WHERE name=:type"
    if type != None and system != None:
        inst += " AND"
    if system != None:
        if type == None:
            inst += " WHERE"
        inst += " system=:system"
        sys = system.upper()

    emb = dis.Embed(colour=dis.Color.dark_orange(), title=titletext, description="Currently tracked planetaries:")
    anoms = db_cursor.execute(inst, {"type": type, "system": sys}).fetchall()
    print(anoms)
    for anom in anoms:
        emb.add_field(str(anom[0]) + "-" + str(anom[1]), "**System:** " + str(anom[2]).capitalize() + "\n**Planet:** " + str(anom[3]) + "\n**Notes:** " + str(anom[4]) + "\n**Discovered on:** <t:" + str(int(anom[5])) + "> (<t:" + str(int(anom[5])) + ":R>)")
    await inter.response.send_message(embed=emb)

@bot.slash_command()
async def remove(inter):
    pass

@remove.sub_command(description="Delete an anomaly from the bot's database")
async def anomaly(inter, number: int, system: str, scope: str = ''):
    gid = ''
    if scope.strip().upper() != "GLOBAL":
        gid += str(inter.guild_id)
    sys = db_cursor.execute(f"SELECT * FROM anomalies{gid} WHERE number=:number AND system=:system", {"number": number, "system": system.upper()}).fetchone()
    db_cursor.execute(f"DELETE FROM anomalies{gid} WHERE number=:number AND system=:system", {"number": number, "system": system.upper()})
    if sys[0] in ["WH", "S-WH"]:
        db_cursor.execute(f"DELETE FROM anomalies{gid} WHERE number=:number AND notes=:notes", {"number": number, "notes": "Leads to " + system.capitalize()})
    database.commit()
    await inter.response.send_message("Anomaly deleted!")

@remove.sub_command(description="Delete an aberration from the bot's database")
async def planetary(inter, number: int, system: str, type: str = planetary_abbr, scope: str = ''):
    gid = ''
    if scope.strip().upper() != "GLOBAL":
        gid += str(inter.guild_id)
    instruction = f"DELETE FROM aberrations{gid} WHERE number=:number AND system=:system"
    if type != None:
        instruction += f" AND type={type}"
    db_cursor.execute(instruction, {"number": number, "system": system.upper()})
    database.commit()
    await inter.response.send_message("Anomaly deleted!")

@bot.slash_command(description="Edit the note of an system/planetary anomaly")
async def note(inter, note: str, number: int, system: str, type: str = commands.Param(choices=["anomaly", "planetary"]), scope: str = ''):
    gid = ''
    if scope.strip().upper() != "GLOBAL":
        gid += str(inter.guild_id)
    if type == "anomaly":
        db_cursor.execute(f"UPDATE anomalies{gid} SET notes=:note WHERE number=:number AND system=:system", {"note": note, "number": number, "system": system.upper()})
    else:
        db_cursor.execute(f"UPDATE aberrations{gid} SET notes=:note WHERE number=:number AND system=:system", {"note": note, "number": number, "system": system.upper()})
    database.commit()
    await inter.response.send_message("Note updated!")

keep_alive()
my_secret = os.environ['token']
print("Up and running!")
bot.run(my_secret)