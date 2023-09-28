from imports_and_constants import *


def copy_file(src, dst):
    shutil.copyfile(src, dst)


def load_json(file_name):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except json.decoder.JSONDecodeError:
        if os.path.exists(file_name + ".old"):
            copy_file(file_name + ".old", file_name)
            with open(file_name, "r") as file:
                return json.load(file)
        else:
            # raise json.decoder.JSONDecodeError(
            #     "JSON file is corrupted and no backup exists", "", 0)
            print("JSON file is corrupted and no backup exists")
            return {}



def save_json(file_name, data):
    if os.path.exists(file_name):
        copy_file(file_name, file_name + ".old")

    with open(file_name, "w") as file:
        json.dump(data, file, indent=2)


def initialize_guild(guild):
    guildID = guild.id
    os.mkdir(os.path.join("data/guilds/", str(guildID)))
    save_json(os.path.join("data/guilds/", str(guildID),
              "settings.json"), default_settings)
    save_json(os.path.join("data/guilds/", str(guildID), "meta.json"),
              {
        "name": guild.name,
        "id": guildID,
        "owner": guild.owner_id,
        # "icon": guild.icon,
    })
    save_json(os.path.join("data/guilds/", str(guildID),
              "text_xp.json"), {}) # {"userid": xp}
    save_json(os.path.join("data/guilds/", str(guildID),
              "voice_session_time.json"), {}) # {"userid": time_started}
    save_json(os.path.join("data/guilds/", str(guildID),
              "voice_xp.json"), {}) # {"userid": {"xp": xp, ... etc}}}
    


def change_settings_for_guild(guild, setting, value):
    guildID = guild.id
    if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
        initialize_guild(guild)
    settings = load_json(os.path.join("data/guilds/", str(guildID),"settings.json"))
    settings[setting] = value
    save_json(os.path.join("data/guilds/", str(guildID),"settings.json"), settings)

def get_settings_for_guild(guild):
    guildID = guild.id
    if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
        initialize_guild(guild)
    settings = load_json(os.path.join("data/guilds/", str(guildID),"settings.json"))
    return settings



def get_active_voice_sessions(guild):
    guildID = guild.id
    if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
        initialize_guild(guild)
    voice_session_time = load_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"))
    return voice_session_time # {"userid": time_started, ... etc}

def set_voice_session_start(guild, userID, start):
    guildID = guild.id
    if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
        initialize_guild(guild)
    voice_session_time = load_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"))
    voice_session_time[str(userID)] = start
    save_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"), voice_session_time)


def remove_voice_session_list(guild, list_of_userIDs): # more efficient than calling remove_voice_session for each user
    guildID = guild.id
    if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
        initialize_guild(guild)
    voice_session_time = load_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"))
    for userID in list_of_userIDs:
        del voice_session_time[str(userID)]
    save_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"), voice_session_time)

def remove_voice_session(guild, userID):
    guildID = guild.id
    if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
        initialize_guild(guild)
    voice_session_time = load_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"))
    del voice_session_time[str(userID)]
    save_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"), voice_session_time)


def add_voice_xp(guild, userID, xp):
    guildID = guild.id
    if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
        initialize_guild(guild)
    
    voicexp = load_json(os.path.join("data/guilds/", str(guildID),"voice_xp.json"))
    if not str(userID) in voicexp:
        voicexp[str(userID)] = 0
    voicexp[str(userID)] += xp
    save_json(os.path.join("data/guilds/", str(guildID),"voice_xp.json"), voicexp)


def get_voice_xp(guild, userID):
    guildID = guild.id
    if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
        initialize_guild(guild)
    voicexp = load_json(os.path.join("data/guilds/", str(guildID),"voice_xp.json"))
    if not str(userID) in voicexp:
        return 0
    return voicexp[str(userID)]




def xp_rate(session_time):
    if session_time < 60*5:
        return session_time / (60*5) # 0..1
    if session_time < 60*60*2.5:
        return 1
    return 2**(-((session_time-60*60*2.5)/3600)*2)


def make_embed(title="", description="", color=0x00ff00, footer=None, image=None, thumbnail=None, author=None,
               fields=None, top_icon_url="", bottom_icon_url="", url=""):
    embed = nextcord.Embed(title=title, description=description, color=color, url=url)
    if footer: embed.set_footer(text=footer, icon_url=bottom_icon_url)
    if image:  embed.set_image(url=image)
    if thumbnail: embed.set_thumbnail(url=thumbnail)
    if top_icon_url == None:
        top_icon_url = ""
    if bottom_icon_url == None:
        bottom_icon_url = ""
    if author: embed.set_author(name=author, icon_url=top_icon_url)
    if fields:
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=field[2])
    return embed



if __name__ == "__main__":
    # save_json("test.json", {"cdb": "test"})
    print(load_json("test.json"))
