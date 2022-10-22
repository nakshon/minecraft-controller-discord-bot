import discord

bot = None
_data = {'current_components': [], 'files_panel_component': [], 'teleport_destination': '',
         'log_select_options': [], 'log_select_page': 0}

def data(var, new_value=None):
    """
    Discord components dictionary value reader/setter function.


    """

    global _data

    # To set clear out the value use 0 instead of None. e.g. data('player_selected', 0)
    if new_value is not None: _data[var] = new_value

    if var in _data.keys():
        return _data[var]
    else: return False

async def clear():
    """
    Deletes old components to prevent conflicts.
    When certain panels (e.g. worldrestorepanel) are opened, they will be added to current_components list.
    When new panel is opened the old one is deleted.

    Is needed because if you change something with an old panel when a new one is needed, conflicts may happen.
    e.g. Deleting a listing in a selection box.
    """

    for i in data('current_components'):
        try: await i.delete()
        except: pass
    data('current_components', [])

class Discord_Select(discord.ui.Select):
    def __init__(self, options, custom_id, placeholder='Choose', min_values=1, max_values=1):
        super().__init__(options=options, custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values)

    async def callback(self, interaction):
        await interaction.response.defer()  # Defer response so not to show failed interaction message.
        custom_id = interaction.data['custom_id']
        value = interaction.data['values'][0].strip()

        data(custom_id, value)  # Updates corresponding variables

        if custom_id == 'server_panel1':
            ctx = await bot.get_context(interaction.message)  # Get ctx from message.
            await ctx.invoke(bot.get_command('_update_server_panel'), value)

class Discord_Button(discord.ui.Button):
    """
    Create button from received list containing label, custom_id, and emoji.
    Uses custom_id with ctx.invoke to call corresponding function.
    """

    def __init__(self, label, custom_id, emoji=None, style=discord.ButtonStyle.grey):
        super().__init__(label=label, custom_id=custom_id, emoji=emoji, style=style)

    async def callback(self, interaction):
        await interaction.response.defer()
        custom_id = interaction.data['custom_id']

        # Get parameter for use of command being invoke from custom_id. E.g. 'gamemode player survival'
        params = ['']
        try:
            custom_id_split = custom_id.split(' ')
            custom_id, params = custom_id_split[0], custom_id_split[1:]
        except: pass

        # Runs function of same name as button's .custom_id variable. e.g. _teleport_selected()
        ctx = await bot.get_context(interaction.message)  # Get ctx from message.
        if params:
            if params[0] == 'player': params[0] = data('player_selected')  # Use currently selected player as a parameter
            await ctx.invoke(bot.get_command(custom_id), *params)
        else: await ctx.invoke(bot.get_command(custom_id))

def new_buttons(buttons_list):
    """Create new discord.ui.View and add buttons, then return said view."""

    view = discord.ui.View(timeout=None)
    for button in buttons_list:
        if len(button) == 2: button.append(None)  # For button with no emoji.
        view.add_item(Discord_Button(label=button[0], custom_id=button[1], emoji=button[2]))
    return view

def new_selection(select_options_args, custom_id, placeholder):
    """Create new discord.ui.View, add Discord_Select and populates options, then return said view."""

    view = discord.ui.View(timeout=None)
    select_options = []

    # Create options for select menu.
    for option in select_options_args:
        if len(option) == 2: option += False, None  # Sets default for 'Default' arg for SelectOption.
        elif len(option) == 3: option.append(None)
        select_options.append(discord.SelectOption(label=option[0], value=option[1], default=option[2], description=option[3]))
    view.add_item(Discord_Select(options=select_options, custom_id=custom_id, placeholder=placeholder))
    return view