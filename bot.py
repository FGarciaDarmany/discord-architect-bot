import nextcord
from nextcord.ext import commands, tasks
from dotenv import load_dotenv
import os
from datetime import datetime

# === Cargar variables del .env ===
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
PREMIUM_ROLE_ID = int(os.getenv("PREMIUM_ROLE_ID"))
FREE_ROLE_ID = int(os.getenv("FREE_ROLE_ID"))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))
GESTION_CANAL_ID = int(os.getenv("GESTION_CANAL_ID"))
GENERAL_CHANNEL_ID = int(os.getenv("GENERAL_CHANNEL_ID"))

# === Intents ===
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === FLASK KEEP-ALIVE ===
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "🟢 The Architect está corriendo."

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# === === === TU LÓGICA DEL BOT === === ===

PREMIUM_FILE = "usuarios_premium.txt"
FREE_FILE = "usuarios_free.txt"

def guardar_usuario(file, member):
    with open(file, "a") as f:
        f.write(f"{member.name}#{member.discriminator} | ID: {member.id}\n")

@bot.event
async def on_ready():
    print(f"✅ The Architect conectado como {bot.user}")
    if not recordatorio_pagos.is_running():
        recordatorio_pagos.start()

@bot.event
async def on_member_join(member):
    print(f"👀 Nuevo miembro detectado: {member.name} ({member.id})")
    guild = bot.get_guild(GUILD_ID)
    free_role = guild.get_role(FREE_ROLE_ID)
    general_channel = guild.get_channel(GENERAL_CHANNEL_ID)

    if free_role:
        try:
            await member.add_roles(free_role)
            print(f"✅ Rol Free asignado a {member.name}")
        except nextcord.Forbidden:
            print(f"❌ No tengo permisos para asignar rol Free a {member.name}")

    mensaje = (
        f"👋 ¡Bienvenido/a {member.mention}! Ahora formas parte de los usuarios **Free**.\n"
        "⚠️ Como Free no tendrás acceso a servicios **Premium** como proyecciones, herramientas de trading ni sesiones en vivo.\n"
        "✅ Puedes seguir participando en nuestro canal general y mantenerte conectado con la comunidad.\n"
        "🐇 *Bienvenido a la Matrix. La madriguera del conejo te espera.*"
    )

    if general_channel:
        await general_channel.send(mensaje)
        print(f"✅ Bienvenida publicada en #{general_channel.name}")

    try:
        await member.send(mensaje)
        print(f"✅ Bienvenida enviada por DM a {member.name}")
    except nextcord.Forbidden:
        print(f"❌ No se pudo enviar DM a {member.name} (Privacidad)")

    guardar_usuario(FREE_FILE, member)

# === Verificador de rol admin ===
def es_admin(ctx):
    admin_role = nextcord.utils.get(ctx.guild.roles, id=ADMIN_ROLE_ID)
    return admin_role and admin_role in ctx.author.roles

# === Comando: Subir a Premium ===
@bot.command()
async def premium(ctx, member: nextcord.Member):
    if ctx.channel.id != GESTION_CANAL_ID:
        await ctx.send("🚫 Este comando solo se puede usar en el canal de gestión de usuarios.")
        return

    if not es_admin(ctx):
        await ctx.send("🚫 No tienes permisos para usar este comando.")
        return

    guild = ctx.guild
    premium_role = guild.get_role(PREMIUM_ROLE_ID)
    free_role = guild.get_role(FREE_ROLE_ID)

    if premium_role:
        try:
            await member.add_roles(premium_role)
        except nextcord.Forbidden:
            await ctx.send("❌ No tengo permisos para asignar el rol Premium.")
            return
    if free_role:
        try:
            await member.remove_roles(free_role)
        except nextcord.Forbidden:
            await ctx.send("❌ No tengo permisos para quitar el rol Free.")
            return

    mensaje = (
        f"🟥 **Bienvenido a la élite Premium, {member.mention}!**\n"
        "Como diría Morfeo: *“Lo único que te ofrezco es la verdad, nada más.”*\n"
        "Tomaste la pastilla roja. Has decidido salir de la Matrix.\n"
        "🚀 Gracias por tu confianza, ahora desbloqueas proyecciones, herramientas de trading y sesiones exclusivas.\n"
        "¡Prepárate para ver hasta dónde llega la madriguera del conejo! 🐇"
    )

    await ctx.send(f"✅ {member.mention} ahora es usuario Premium.")
    try:
        await member.send(mensaje)
    except nextcord.Forbidden:
        print(f"❌ No se pudo enviar DM a {member.name}")

    guardar_usuario(PREMIUM_FILE, member)
    print(f"✅ Usuario {member.name} ahora es Premium")

# === Comando: Bajar a Free ===
@bot.command()
async def free(ctx, member: nextcord.Member):
    if ctx.channel.id != GESTION_CANAL_ID:
        await ctx.send("🚫 Este comando solo se puede usar en el canal de gestión de usuarios.")
        return

    if not es_admin(ctx):
        await ctx.send("🚫 No tienes permisos para usar este comando.")
        return

    guild = ctx.guild
    premium_role = guild.get_role(PREMIUM_ROLE_ID)
    free_role = guild.get_role(FREE_ROLE_ID)
    general_channel = guild.get_channel(GENERAL_CHANNEL_ID)

    if premium_role:
        try:
            await member.remove_roles(premium_role)
        except nextcord.Forbidden:
            await ctx.send("❌ No tengo permisos para quitar el rol Premium.")
            return
    if free_role:
        try:
            await member.add_roles(free_role)
        except nextcord.Forbidden:
            await ctx.send("❌ No tengo permisos para asignar el rol Free.")
            return

    mensaje = (
        f"👋 {member.mention}, ahora formas parte de los usuarios **Free**.\n"
        "⚠️ Como Free no tendrás acceso a servicios **Premium** como proyecciones, herramientas de trading ni sesiones en vivo.\n"
        "✅ Puedes seguir participando en nuestro canal general y mantenerte conectado con la comunidad.\n"
        "🐇 *Vuelve a la Matrix cuando estés listo.*"
    )

    if general_channel:
        await general_channel.send(mensaje)

    try:
        await member.send(mensaje)
    except nextcord.Forbidden:
        print(f"❌ No se pudo enviar DM a {member.name}")

    guardar_usuario(FREE_FILE, member)
    print(f"✅ Usuario {member.name} bajado a Free")

# === Tarea recordatorio de pagos ===
@tasks.loop(hours=24)
async def recordatorio_pagos():
    today = datetime.now()
    if today.day == 10:
        guild = bot.get_guild(GUILD_ID)
        admin_role = guild.get_role(ADMIN_ROLE_ID)
        if admin_role:
            for member in admin_role.members:
                try:
                    await member.send(
                        "🔔 *Recuerda...*\n"
                        "Como diría Morfeo: *“Lo único que te ofrezco es la verdad, nada más.”*\n"
                        "🗓️ El día de pago se acerca. Los servicios **Premium** estarán disponibles hasta el día 10.\n"
                        "⛔ El día 11, si no hay pago, perderás tu acceso Premium.\n"
                        "Prepárate para decidir si quieres seguir en la Matrix o salir de ella. 🐇✨"
                    )
                except nextcord.Forbidden:
                    print(f"❌ No se pudo enviar recordatorio a {member.name} (Privacidad)")

# === Ejecutar Bot ===
bot.run(TOKEN)
