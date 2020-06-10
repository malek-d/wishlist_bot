import discord, sys
from datetime import datetime
from discord.ext import commands
from config.EnvironmentCfg import getFirebaseToken
from db.firebaseConnector import Firebase

class Wishlist(commands.Cog):

    def __init__(self, client):
        self.client = client
        fb_token = getFirebaseToken()
        self.fb = Firebase(fb_token)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        command_str = """
            $wishlist\n
            $add\n
            $remove\n
            $update\n
        """
        definition_str = """
            Retrieves users current wishlist - e.g. $wishlist OR $wishlist @user\n
            Adds a new item to your wishlist - e.g $add Portal 2 \n
            Remove an item from your wishlist - e.g $remove 4 (To get item number use $wishlist first)\n
            Updates a current item in your wishlist - e.g $update 2 pizza\n
        """
        embed = discord.Embed(title="Wishlist Bot Help", colour=0xA63232)
        embed.add_field(name="Commands", value=command_str, inline=True)
        embed.add_field(name="Definition", value=definition_str, inline=True)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online")
 
    @commands.command()
    async def wishlist(self, ctx):
        user = ""
        if str(ctx.message.content).strip() == "$wishlist":
            user = ctx.message.author
        else:
            try:
                user = ctx.message.mentions[0]
            except IndexError:
                user = None
                print("No users were mentioned")
        str_user = str(user)
        wishlist = self.fb.firebasedb.child("users").child(str_user.replace("#","_")).child("wishlist").get()
        embed = discord.Embed(title="{0}'s wishlist".format(str_user), colour=0x351330)
        if str_user == "None":
            await ctx.send("User does not exist!")
        elif wishlist.val() == None:          
            await ctx.send("{0}'s wishlist is empty!".format(str_user))
        else:
            count = 1
            item_field = ""
            date_field = ""
            for item in wishlist.each():
                content = item.val()
                if content is None:
                    next
                else:
                    item_field = item_field + "{0} - {1}\n".format(count, content['item'])
                    date_field = date_field + "{0}\n".format(content['date'])
                    count = count + 1
            embed.add_field(name="Wishlist Items", value=item_field, inline=True)
            embed.add_field(name="Date Added", value=date_field, inline=True)
            await ctx.send("Here is {0}'s wishlist {1}".format(str_user,ctx.message.author.mention))
            await ctx.send(embed=embed)
    
    @commands.command()
    async def add(self,ctx) :
        item = str(ctx.message.content.replace('$add', '')).strip()
        user = str(ctx.message.author).replace('#','_')
        time = datetime.now()
        item_dict = {"item": item, "date": time.strftime("%d/%m/%Y %H:%M") }

        items = self.fb.firebasedb.child("users").child(user).child("wishlist").get()
        if items.val() == None:
            self.fb.firebasedb.child("users").child(user).child("wishlist").child("0").set(item_dict)
            self.fb.firebasedb.child("users").child(user).child("wishlist_count").set({'items': 1})
        else:
            current_count = self.fb.firebasedb.child("users").child(user).child("wishlist_count").get()
            current_count = current_count.val()
            current_count = current_count['items']
            self.fb.firebasedb.child("users").child(user).child("wishlist").child(len(items.val())).set(item_dict)
            self.fb.firebasedb.child("users").child(user).child("wishlist_count").set({'items': int(current_count) + 1})
        await ctx.send("Added to wishlist!")
    
    @commands.command()
    async def kill(self, ctx):
        if str(ctx.message.author) == "Xera#1533":
            await ctx.bot.logout()
        else:
            await ctx.send("You have no power here {0} :^)".format(ctx.message.author.mention))
    
    @commands.command()
    async def remove(self, ctx):
        item = str(ctx.message.content.replace('$remove', '')).strip()
        user = str(ctx.message.author).replace('#','_')
        try:
            item_num = int(item)
            current_count = self.fb.firebasedb.child("users").child(user).child("wishlist_count").get()
            current_count = current_count.val()
            current_count = int(current_count['items'])

            if current_count < item_num or item_num < 1 :
                await ctx.send("Number out of range. Current range for user 1-{0}".format(current_count))
            else:
                wishlist = self.fb.firebasedb.child("users").child(user).child("wishlist").get()
                index = 0
                iter_count = 1
                updated_dict = {}
                for items in wishlist.each():
                    content = items.val()
                    if item_num == iter_count:
                        await ctx.send("{0} has been removed!".format(content['item']))
                    else:
                        updated_dict[str(index)] = {'date': content['date'], 'item': content['item']}
                        index += 1
                    iter_count += 1
                print(updated_dict)
                self.fb.firebasedb.child("users").child(user).child("wishlist").set(updated_dict) if updated_dict is not None else print("No more items for user in db")
                self.fb.firebasedb.child("users").child(user).child("wishlist_count").set({'items': str(index + 1)})
        except ValueError as verr:
            await ctx.send("Message must include a number only")

    @commands.command()
    async def update(self, ctx):
        item = str(ctx.message.content.replace('$update', '')).strip()
        user = str(ctx.message.author)
        user_id = user.replace('#','_')
        time = datetime.now()
        content = item.split(" ")
        try:
            item_num = int(content[0])
            content.pop(0)
            updated_item = " ".join(content)
            current_count = self.fb.firebasedb.child("users").child(user_id).child("wishlist_count").get()
            current_count = current_count.val()
            current_count = int(current_count['items'])
            if current_count < item_num or item_num < 1 :
                await ctx.send("Number out of range. Current range for user 1-{0}".format(current_count))
            else:
                wishlist = self.fb.firebasedb.child("users").child(user_id).child("wishlist").get()
                index = 0
                iter_count = 1
                updated_dict = {}
                for items in wishlist.each():
                    content = items.val()
                    if item_num == iter_count:
                        updated_dict[str(index)] = {'date': time.strftime("%d/%m/%Y %H:%M"), 'item': updated_item}
                        await ctx.send("{0} has been updated to {1}!".format(content['item'], updated_item))
                    else:
                        updated_dict[str(index)] = {'date': content['date'], 'item': content['item']}
                    index += 1
                    iter_count += 1
                print("wut")
                self.fb.firebasedb.child("users").child(user_id).child("wishlist").set(updated_dict) if updated_dict is not None else print("No more items for user in db")
                self.fb.firebasedb.child("users").child(user_id).child("wishlist_count").set({'items': str(index)})
                print(updated_dict)
        except ValueError as verr:
            await ctx.send("To update an exising item please use the following syntax. \"$update <item_num> <new_item_content>\"")


    @commands.command()
    async def commands(self, ctx):
        command_str = """
            $wishlist\n
            $add\n
            $remove\n
            $update\n
        """
        definition_str = """
            Retrieves users current wishlist - e.g. $wishlist OR $wishlist @user\n
            Adds a new item to your wishlist - e.g $add Portal 2 \n
            Remove an item from your wishlist - e.g $remove 4 (To get item number use $wishlist first)\n
            Updates a current item in your wishlist - e.g $update 2 pizza\n
        """
        embed = discord.Embed(title="Wishlist Bot Help", colour=0x4BB543)
        embed.add_field(name="Commands", value=command_str, inline=True)
        embed.add_field(name="Definition", value=definition_str, inline=True)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Wishlist(client))