"""
Bot d'accueil Assistant FM.

Fonction :
  - À chaque nouveau membre, envoie un message de bienvenue dans un salon.
  - Commande !accueil-test pour tester le rendu.

Prérequis :
  1. pip install discord.py
  2. Portail développeur → ton application → Bot → activer :
       - SERVER MEMBERS INTENT  (obligatoire pour on_member_join)
       - MESSAGE CONTENT INTENT (pour la commande de test)
  3. Inviter le bot avec les permissions : Voir les salons, Envoyer des messages,
     Lire l'historique, Gérer les salons (optionnel).
  4. Variables d'environnement (dans le même terminal) :
       $env:DISCORD_TOKEN = "..."
       $env:DISCORD_GUILD_ID = "..."          # optionnel
       $env:WELCOME_CHANNEL = "👋 présentations"  # optionnel
  5. Lancer : python bot_assistant_fm.py
"""

import os

import discord
from discord.ext import commands

TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID") or "0")
WELCOME_CHANNEL = os.environ.get("WELCOME_CHANNEL", "👋 présentations")

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
    """Trouve le salon d'accueil, sinon #général, sinon le premier salon texte."""
    channel = discord.utils.get(guild.text_channels, name=WELCOME_CHANNEL)
    if channel is not None:
        return channel
    channel = discord.utils.get(guild.text_channels, name="💬 général")
    if channel is not None:
        return channel
    return next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)


def construire_embed(member):
    guild = member.guild
    def mention(nom):
        ch = discord.utils.get(guild.text_channels, name=nom)
        return ch.mention if ch else f"#{nom}"

    embed = discord.Embed(
        title="👋 Bienvenue sur Assistant FM !",
        description=(
            f"Salut {member.mention} !\n\n"
            "**Assistant FM** est l'assistant d'analyse pour **Football Manager 2027** : "
            "extraction des sauvegardes `.fm`, recrutement, tactique, suivi de carrière.\n\n"
            "📍 **Commence ici :**\n"
            f"• Présente-toi → {mention('👋 présentations')}\n"
            f"• Raconte ta partie → {mention('📖 ma-partie')}\n"
            f"• Questions / bugs → {mention('❓ aide')} · {mention('🐛 bugs')}\n\n"
            f"⬇️ **Téléchargement Windows :** {DOWNLOAD_URL}"
        ),
        color=0x5B9BD5,
    )
    try:
        embed.set_thumbnail(url=member.display_avatar.url)
    except Exception:
        pass
    embed.set_footer(text="Assistant FM · discord.gg/YR2e8kMHeF")
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
        print(f"Permission refusée dans {channel.name}.")
        return False


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} (ID {bot.user.id})")
    print("Bot d'accueil prêt. Les nouveaux membres recevront un message.")


@bot.event
async def on_member_join(member):
    if member.bot:
        return
    ok = await envoyer_accueil(member)
    if ok:
        print(f"Accueil envoyé à {member} ({member.id}).")


@bot.command(name="accueil-test")
@commands.has_permissions(manage_guild=True)
async def accueil_test(ctx):
    """Teste le message d'accueil sur le salon configuré."""
    ok = await envoyer_accueil(ctx.author)
    if ok:
        await ctx.send("✅ Message d'accueil envoyé.")
    else:
        await ctx.send("⚠️ Impossible d'envoyer le message (salon ou permission manquants).")


def main():
    token = nettoyer_token(TOKEN)
    if not token:
        raise SystemExit("DISCORD_TOKEN manquant.")
    if token.count(".") != 2 or len(token) < 50:
        raise SystemExit("Token invalide : copie le token du bot (Bot → Reset Token).")
    bot.run(token)


if __name__ == "__main__":
    main()