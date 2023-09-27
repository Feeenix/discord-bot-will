from xp_related import *



@client.slash_command(name="settings",description="run this command without args to see current settings, or with args to change them",
)
async def test(interaction: Interaction,  
# midifile_attachment:nextcord.Attachment = SlashOption(description="Midi file to be converted.", required = True, name="midifile_attachment"),
# longnote:float = SlashOption(description="Sustain factor. Higher values = longer sustains. Defaults to 5", required = False,default=5, name="longnote", choices={"0": 0, "1": 1, "2": 2,"3" : 3, "4" : 4, "5 (Default)": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10 }),
# timemultiply:float = SlashOption(description="Time factor. Higher values = longer songs. Defaults to 1.0", required = False,default=1.0, name="timemultiply", min_value=0.1, max_value=10.0),
# spawnproof:int = SlashOption(description="Toggles blocking monster spawning. Defaults to false", required = False,default=False, name="spawnproof", choices = {"true": True, "false (Default)": False}),
# tracks:int = SlashOption(description="*EXPERIMENTAL!* The number of tracks to spread notes between. Default is 14", required = False,default=14, name="tracks", choices = {"1": 1, "2": 2, "3": 3,"4" : 4, "5" : 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "11": 11, "12": 12, "13": 13, "14 (Default)": 14, "15": 15, "16": 16}),
# mp3:int = SlashOption(description="*EXPERIMENTAL!* Export as audio instead of litematic. Defaults to litematic", required = False,default=False, name="audio", choices = {"Audio file": True, "Litematica file (Default)": False}),


setting:str = SlashOption(description="The name of the setting you want to change", required = False, default="", name="setting", choices={"voicexp": "voicexp", "messagexp": "messagexp"}),
value:int = SlashOption(description="the value of the setting, in case of booleans then 0 means false and 1 means true", required = False,default=0, name="value"),
):
    # interaction.response.defer() # let the user know we're working on it
    await interaction.response.send_message("working on it")
    return