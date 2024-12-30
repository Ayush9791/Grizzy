import discord
from discord.ext import commands
import random
import asyncio

class NumberGuess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.group(invoke_without_command=True)
    async def guess(self, ctx):
        await ctx.send("Use `~guess start` to start a game, or `~guess help` for more info.")

    @guess.command()
    async def start(self, ctx):
        if ctx.guild.id in self.active_games:
            await ctx.send("A game is already in progress in this server. Use `~guess stop` to end it.")
            return
        
        number_to_guess = random.randint(1, 6)
        self.active_games[ctx.guild.id] = {
            'number': number_to_guess,
            'attempts': 0,
            'players': {}
        }
        await ctx.send("I've chosen a number between 1 and 6. Try to guess it!")

    @guess.command()
    async def stop(self, ctx):
        if ctx.guild.id not in self.active_games:
            await ctx.send("No game is currently in progress.")
            return
        
        del self.active_games[ctx.guild.id]
        await ctx.send("The game has been stopped.")

    @guess.command()
    async def help(self, ctx):
        help_message = (
            "`!guess start` - Start a new number guessing game.\n"
            "`!guess stop` - Stop the current game.\n"
            "`!guess <number>` - Make a guess."
        )
        await ctx.send(help_message)

    @guess.command()
    async def number(self, ctx, guess: int):
        if ctx.guild.id not in self.active_games:
            await ctx.send("No game is currently in progress. Use `~guess start` to begin.")
            return
        
        game = self.active_games[ctx.guild.id]
        game['attempts'] += 1

        if guess < game['number']:
            await ctx.send("Too low! Try again.")
        elif guess > game['number']:
            await ctx.send("Too high! Try again.")
        else:
            await ctx.send(f"Congratulations {ctx.author.mention}! You've guessed the number {game['number']} in {game['attempts']} attempts!")
            del self.active_games[ctx.guild.id]
    
class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deck = self.create_deck()

    def create_deck(self):
        suits = ['<:ACEOFHEART:1286014692090712126>','<:ACEOFDIAMOND:1286014634830069901>', '<:ACEOFCLUB:1286014660830826578>', '<:ACEOFSPADE:1286014676429439007>']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        deck = [(rank, suit) for rank in ranks for suit in suits]
        random.shuffle(deck)
        return deck

    def calculate_hand_value(self, hand):
        value = 0
        aces = 0
        for card, _ in hand:
            if card in ['Jack', 'Queen', 'King']:
                value += 10
            elif card == 'Ace':
                aces += 1
                value += 11
            else:
                value += int(card)
        
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    @commands.command(name='blackjack')
    async def blackjack(self, ctx):
        if not hasattr(ctx, 'game_active'):
            ctx.game_active = True
            player_hand = [self.deck.pop(), self.deck.pop()]
            dealer_hand = [self.deck.pop(), self.deck.pop()]
            player_value = self.calculate_hand_value(player_hand)
            dealer_value = self.calculate_hand_value(dealer_hand)

            await ctx.send(f"Your hand: {player_hand} (Value: {player_value})")
            await ctx.send(f"Dealer's hand: [{dealer_hand[0]}, Hidden]")

            while player_value < 21:
                await ctx.send("Type `~hit` to draw a card or `~stand` to hold.")
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.send("Time's up! You lose.")
                    return
                
                if msg.content.lower() == '~hit'or'bjhit':
                    player_hand.append(self.deck.pop())
                    player_value = self.calculate_hand_value(player_hand)
                    await ctx.send(f"You drew: {player_hand[-1]}. Your hand: {player_hand} (Value: {player_value})")
                elif msg.content.lower() == '~stand'or'bjstand':
                    break

            while dealer_value < 17:
                dealer_hand.append(self.deck.pop())
                dealer_value = self.calculate_hand_value(dealer_hand)

            await ctx.send(f"Dealer's hand: {dealer_hand} (Value: {dealer_value})")
            await self.determine_winner(ctx, player_value, dealer_value)
        else:
            await ctx.send("A game is already in progress!")

    async def determine_winner(self, ctx, player_value, dealer_value):
        if player_value > 21:
            await ctx.send("You bust! Dealer wins.")
        elif dealer_value > 21 or player_value > dealer_value:
            await ctx.send("You win!")
        elif player_value < dealer_value:
            await ctx.send("Dealer wins!")
        else:
            await ctx.send("It's a tie!")

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.command(name="rps")
    async def rps(self, ctx, opponent: str = None):
        if opponent is None:
            await ctx.send("Please specify whether you want to play against `bot` or challenge another `@member`.")
            return

        # Play against the bot
        if opponent.lower() == "bot":
            await self.play_against_bot(ctx)
        else:
            # Try to find a member in the server
            member = await commands.MemberConverter().convert(ctx, opponent)
            if member:
                await self.play_against_member(ctx, member)
            else:
                await ctx.send("You need to specify either 'bot' or mention a server member to play against.")

    async def play_against_bot(self, ctx):
        await ctx.send("You are playing Rock, Paper, Scissors against the bot! Please type `rock`, `paper`, or `scissors`.")

        def check(msg):
            return msg.author == ctx.author and msg.content.lower() in ['rock', 'paper', 'scissors'] and msg.channel == ctx.channel

        try:
            # Wait for the player's response
            player_response = await self.bot.wait_for('message', check=check, timeout
                                                      =60.0)
        except TimeoutError:
            await ctx.send("You took too long to respond!")
            return

        player_choice = player_response.content.lower()
        bot_choice = random.choice(['rock', 'paper', 'scissors'])

        result = self.determine_winner(player_choice, bot_choice)

        # Announce the result
        if result == "win":
            await ctx.send(f"You chose **{player_choice}**, I chose **{bot_choice}**. You win! 🎉")
        elif result == "lose":
            await ctx.send(f"You chose **{player_choice}**, I chose **{bot_choice}**. I win! 😎")
        else:
            await ctx.send(f"We both chose **{player_choice}**. It's a tie! 🤝")

    async def play_against_member(self, ctx, opponent: discord.Member):
        if opponent == ctx.author:
            await ctx.send("You can't challenge yourself!")
            return

        if opponent.bot:
            await ctx.send("You can't challenge a bot!")
            return

        # Check if either player is in an active game
        if ctx.author.id in self.active_games or opponent.id in self.active_games:
            await ctx.send("One of the players is already in an active game.")
            return

        # Start the game and send DM instructions
        self.active_games[ctx.author.id] = None
        self.active_games[opponent.id] = None

        await ctx.send(f"{opponent.mention}, you have been challenged to a game of Rock, Paper, Scissors! Check your DMs to play.")
        await ctx.author.send("You have challenged someone to a game of Rock, Paper, Scissors! Reply with `rock`, `paper`, or `scissors` to play.")
        await opponent.send(f"You have been challenged to a game of Rock, Paper, Scissors by {ctx.author.display_name}! Reply with `rock`, `paper`, or `scissors` to play.")

        def check(msg):
            return msg.author.id in self.active_games and msg.content.lower() in ["rock", "paper", "scissors"]

        try:
            player1_response = await self.bot.wait_for('message', check=check, timeout=60.0)
            self.active_games[ctx.author.id] = player1_response.content.lower()

            player2_response = await self.bot.wait_for('message', check=check, timeout=60.0)
            self.active_games[opponent.id] = player2_response.content.lower()

        except TimeoutError:
            await ctx.send("The game timed out as one of the players didn't respond in time.")
            self.active_games.pop(ctx.author.id, None)
            self.active_games.pop(opponent.id, None)
            return

        player1_choice = self.active_games[ctx.author.id]
        player2_choice = self.active_games[opponent.id]

        result = self.determine_winner(player1_choice, player2_choice)

        if result == "win":
            message = f"{ctx.author.display_name} chose **{player1_choice}**, {opponent.display_name} chose **{player2_choice}**. {ctx.author.mention} wins! 🎉"
        elif result == "lose":
            message = f"{ctx.author.display_name} chose **{player1_choice}**, {opponent.display_name} chose **{player2_choice}**. {opponent.mention} wins! 🎉"
        else:
            message = f"Both players chose **{player1_choice}**. It's a tie! 🤝"

        await ctx.send(message)

        self.active_games.pop(ctx.author.id, None)
        self.active_games.pop(opponent.id, None)

    def determine_winner(self, player1_choice, player2_choice):
        if player1_choice == player2_choice:
            return "tie"
        elif (player1_choice == "rock" and player2_choice == "scissors") or \
             (player1_choice == "scissors" and player2_choice == "paper") or \
             (player1_choice == "paper" and player2_choice == "rock"):
            return "win"
        else:
            return "lose"

async def setup(bot):
    await bot.add_cog(Blackjack(bot))
    await bot.add_cog(NumberGuess(bot))
    await bot.add_cog(RockPaperScissors(bot))




    