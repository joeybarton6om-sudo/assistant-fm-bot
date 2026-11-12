"""
Bot d'accueil Assistant FM.

Fonction :
  - Ã€ chaque nouveau membre, envoie un message de bienvenue dans un salon.
  - Commande !accueil-test pour tester le rendu.

PrÃ©requis :
  1. pip install discord.py
  2. Portail dÃ©veloppeur â†’ ton application â†’ Bot â†’ activer :
       - SERVER MEMBERS INTENT  (obligatoire pour on_member_join)
       - MESSAGE CONTENT INTENT (pour la commande de test)
  3. Inviter le bot avec les permissions : Voir les salons, Envoyer des messages,
     Lire l'historique, GÃ©rer les salons (optionnel).
  4. Variables d'environnement (dans le mÃªme terminal) :
       $env:DISCORD_TOKEN = "..."
       $env:DISCORD_GUILD_ID = "..."          # optionnel
       $env:WELCOME_CHANNEL = "ðŸ‘‹ prÃ©sentations"  # optionnel
  5. Lancer : python bot_assistant_fm.py
"""

import os

import discord
from discord.ext import commands

TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID") or "0")
WELCOME_CHANNEL = os.environ.get("WELCOME_CHANNEL", "ðŸ‘‹ prÃ©sentations")

DOWNLOAD_URL = "https://www.dropbox.com/t/Gz5RY46Ncc7brDVM"


def nettoyer_token(valeur):
    if not valeur:
        return ""
    t = valeur.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        t = t[1:-1].strip()
    if t.lower().startswith("bot "):
        t = t[4:].strip()
    return t


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def trouver_salon_accueil(guild):
    """Trouve le salon d'accueil, sinon #gÃ©nÃ©ral, sinon le premier salon texte."""
    channel = discord.utils.get(guild.text_channels, name=WELCOME_CHANNEL)
    if channel is not None:
        return channel
    channel = discord.utils.get(guild.text_channels, name="ðŸ’¬ gÃ©nÃ©ral")
    if channel is not None:
        return channel
    return next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)


def construire_embed(member):
    guild = member.guild
    def mention(nom):
        ch = discord.utils.get(guild.text_channels, name=nom)
        return ch.mention if ch else f"#{nom}"

    embed = discord.Embed(
        title="ðŸ‘‹ Bienvenue sur Assistant FM !",
        description=(
            f"Salut {member.mention} !\n\n"
            "**Assistant FM** est l'assistant d'analyse pour **Football Manager 2027** : "
            "extraction des sauvegardes `.fm`, recrutement, tactique, suivi de carriÃ¨re.\n\n"
            "ðŸ“ **Commence ici :**\n"
            f"â€¢ PrÃ©sente-toi â†’ {mention('ðŸ‘‹ prÃ©sentations')}\n"
            f"â€¢ Raconte ta partie â†’ {mention('ðŸ“– ma-partie')}\n"
            f"â€¢ Questions / bugs â†’ {mention('â“ aide')} Â· {mention('ðŸ› bugs')}\n\n"
            f"â¬‡ï¸ **TÃ©lÃ©chargement Windows :** {DOWNLOAD_URL}"
        ),
        color=0x5B9BD5,
    )
    try:
        embed.set_thumbnail(url=member.display_avatar.url)
    except Exception:
        pass
    embed.set_footer(text="Assistant FM Â· discord.gg/YR2e8kMHeF")
    return embed


async def envoyer_accueil(member):
    channel = trouver_salon_accueil(member.guild)
    if channel is None:
        print("Aucun salon d'accueil accessible.")
        return False
    try:
        await channel.send(content=member.mention, embed=construire_embed(member))
        return True
    except discord.Forbidden:
        print(f"Permission refusÃ©e dans {channel.name}.")
        return False


@bot.event
async def on_ready():
    print(f"ConnectÃ© en tant que {bot.user} (ID {bot.user.id})")
    print("Bot d'accueil prÃªt. Les nouveaux membres recevront un message.")


@bot.event
async def on_member_join(member):
    if member.bot:
        return
    ok = await envoyer_accueil(member)
    if ok:
        print(f"Accueil envoyÃ© Ã  {member} ({member.id}).")


@bot.command(name="accueil-test")
@commands.has_permissions(manage_guild=True)
async def accueil_test(ctx):
    """Teste le message d'accueil sur le salon configurÃ©."""
    ok = await envoyer_accueil(ctx.author)
    if ok:
        await ctx.send("âœ… Message d'accueil envoyÃ©.")
    else:
        await ctx.send("âš ï¸ Impossible d'envoyer le message (salon ou permission manquants).")


def main():
    token = nettoyer_token(TOKEN)
    if not token:
        raise SystemExit("DISCORD_TOKEN manquant.")
    if token.count(".") != 2 or len(token) < 50:
        raise SystemExit("Token invalide : copie le token du bot (Bot â†’ Reset Token).")
    bot.run(token)


if __name__ == "__main__":
    main()