import aiosonic; import asyncio; import discum; ok_status = [200, 201, 204];
def black(): return '\u001b[30;1m';
def red(): return '\u001b[31;1m';
def green(): return '\u001b[32;1m';
def yellow(): return '\u001b[33;1m';
def blue(): return '\u001b[34;1m';
def magenta(): return '\u001b[35;1m';
def cyan(): return '\u001b[36;1m';
def white(): return '\u001b[37;1m';
def reset(): return '\u001b[0m';
def b_black(): return '\u001b[40;1m';
def b_red(): return '\u001b[41;1m';
def b_green(): return '\u001b[42;1m';
def b_yellow(): return '\u001b[43;1m';
def b_blue(): return '\u001b[44;1m';
def b_magenta(): return '\u001b[45;1m';
def b_cyan(): return '\u001b[46;1m';
def b_white(): return '\u001b[47;1m';
def __headers__(token:str, bot=False) -> set:
    if not bot: return {"Authorization": token};
    return {"Authorization": "Bot "+token};
def members_scrape(guid:str, chid:str, token:str, logs:bool=False) -> list:
    bot = discum.Client(token=token);
    def close_after_fetching(resp, guild_id):
        try:
            if bot.gateway.finishedMemberFetching(guild_id):
                try:
                    lenmembersfetched = len(bot.gateway.session.guild(guild_id).members);
                except Exception as _: return [];
                if logs: print(str(lenmembersfetched)+' members fetched');
                bot.gateway.removeCommand({'function': close_after_fetching, 'params': {'guild_id': guild_id}}); bot.gateway.close()
        except: pass;
    def get_members(guild_id, channel_id):
        try:
            bot.gateway.fetchMembers(guild_id, channel_id, keep="all", wait=1); bot.gateway.command({'function': close_after_fetching, 'params': {'guild_id': guild_id}});
            bot.gateway.run(); bot.gateway.resetSession();
            return bot.gateway.session.guild(guild_id).members;
        except: pass;
    if logs: print('MEMBER SCRAPER\nCredits to https://github.com/Merubokkusu/Discord-S.C.U.M');
    members = get_members(guid, chid);
    if logs:
        for memberID in members: print(memberID);
    f = open("users.txt", "a");
    for element in members: f.write(element + "\n");
    f.close();
    return members;
async def send_dm(message:str="", user_id:str="", delay:int=0):
    if not user_id.isnumeric(): print("Invalid ID."); return 0x1;
    if message == "": message = "**https://www.youtube.com/channel/UCtZgbOCDmuLMquz5Rka9blQ**";
    r = await aiosonic.HTTPClient().post(f"https://discord.com/api/v9/users/@me/channels", json={"recipients": [user_id]}, headers=__headers__(_token, bot=bot_or_user));
    while True:
        if r.status_code in ok_status:
            break;
        elif r.status_code == 429: m = await r.json(); print("[-] Rate Limited"); await asyncio.sleep(float(m['retry_after']));
        else: print("Failed to fetch '%s' with status code of: %s; error: %s" % (user_id, r.status_code, await r.json())); return;
    try: jsonn = await r.json(); dm_id = jsonn['id'];
    except KeyError: return;
    try:
        while True:
            r = await aiosonic.HTTPClient().post("https://discord.com/api/v9/channels/%s/messages" % dm_id, json={"content": "%s" % message}, headers=__headers__(_token, bot=bot_or_user));
            if r.status_code in ok_status:
                print("[+] Sent message to %s" % user_id);
                try:
                    members.remove(user_id);
                    with open("users.txt", "w") as file_:
                        for l in members: file_.write("%s\n" % l);
                except:
                    pass;
                break;
            elif r.status_code == 429:
                m = await r.json(); print("[-] Rate Limited, waiting %s seconds.." % m['retry_after']); await asyncio.sleep(float(m['retry_after']));
            else: print("[/] Failed to DM user: '%s'" % user_id); return 0x1;
    except Exception as ddx: print(ddx);
    await asyncio.sleep(delay);
    return 0x0;
def update_txt(guild, channel, token):
    try: open("users.txt", "w").close();
    except Exception as x: print("Failed to wipe file"); return;
    try:
        members_scrape(guid=str(guild), chid=str(channel), token=_token, logs=False);
    except Exception as y:
        print("An error occured, %s" % y);
        return [];
    with open("users.txt", "r", encoding="UTF-8") as scraped_: scraped = scraped_.read().splitlines();
    scraped_.close(); __import__("os").system("cls" if __import__("os").name == "nt" else "clear");
    return scraped;
async def main():
    global bot_or_user; global members; global _token;
    print("""

    [ Mass DM Tool - By Takaso ]

    [ %sWarning%s: Use a phone verified account! ]

""" % (red(), reset()));
    bot_or_user = False; _token = input("Insert the token of the account > ").replace(" ", "");
    if input("Scrape members? y/n > ").lower().startswith("y"):
        members = update_txt(input("Input the guild ID > "), input("Input the channel ID > "), _token);
    else:
        with open("users.txt", "r", encoding="UTF-8") as scraped_: members = scraped_.read().splitlines();
        scraped_.close();
    if members != []:
        message = input("Choose the message to DM > "); delay = int(input("Choose the delay in seconds > "));
        try: members.remove(str(__import__("base64").b64decode(_token.split(".")[0]+"==").decode("utf-8")));
        except: pass;
        for member in members:
            await send_dm(message, member, delay);
    return input();
asyncio.run(main());