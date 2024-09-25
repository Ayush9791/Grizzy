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
        """Create a deck of cards."""
        suits = ['<:ACEOFHEART:1286014692090712126>','<:ACEOFDIAMOND:1286014634830069901>', '<:ACEOFCLUB:1286014660830826578>', '<:ACEOFSPADE:1286014676429439007>']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        deck = [(rank, suit) for rank in ranks for suit in suits]
        random.shuffle(deck)
        return deck

    def calculate_hand_value(self, hand):
        """Calculate the total value of a hand."""
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

def setup(bot):
    bot.add_cog(NumberGuess(bot))
    bot.add_cog(Blackjack(bot))