from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes
from telegram.ext import filters
import requests
import json
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les valeurs depuis les variables d'environnement
API_KEY = os.getenv("API_KEY")
NEWS_API_URL = os.getenv("NEWS_API_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Dictionnaire pour suivre les usernames
usernames = set(
)  # Utilisation d'un set pour éviter les doublons (un utilisateur ne sera compté qu'une seule fois)

# ID ou Username de l'utilisateur autorisé
AUTHORIZED_USER = "wizyydev"  # Remplacer par le username ou ID autorisé (dans ce cas, un username)


# Start Command
async def start(update, context):
    user_username = update.message.from_user.username  # Récupérer le username de l'utilisateur
    usernames.add(user_username)  # Ajouter le username de l'utilisateur au set
    await update.message.reply_text(
        "Welcome! Send your query in the format: 'query,page_size'.")


# Search News Command
async def search_news(update, context):
    try:
        user_username = update.message.from_user.username  # Récupérer le username de l'utilisateur
        usernames.add(
            user_username)  # Ajouter le username de l'utilisateur au set

        user_input = update.message.text
        query, page_size = user_input.split(",")
        page_size = int(page_size)

        if not (1 <= page_size <= 90000):
            await update.message.reply_text(
                "Page size must be between 1 and 10.")
            return

        headers = {"x-api-token": API_KEY, "Content-Type": "application/json"}
        payload = {"q": query.strip(), "lang": "en", "page_size": page_size}

        response = requests.post(NEWS_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        articles = data.get("articles", [])
        if not articles:
            await update.message.reply_text("No articles found for your query."
                                            )
            return

        # Send each article to the user
        for article in articles:
            title = article.get("title", "No Title")
            author = article.get("author", "Unknown Author")
            source = article.get("name_source", "Unknown Source")
            link = article.get("link", "#")
            message = f"*{title}*\nAuthor: {author}\nSource: {source}\n[Read More]({link})"
            await update.message.reply_markdown(message)

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")


# Command to get the usernames who have interacted with the bot
async def get_usernames(update, context):
    # Vérifier si l'utilisateur est autorisé à accéder à cette commande
    if update.message.from_user.username == AUTHORIZED_USER:
        user_names_list = '\n'.join(
            usernames)  # Joindre les usernames dans un format lisible
        if not user_names_list:
            user_names_list = "No users have interacted yet."
        await update.message.reply_text(
            f"Usernames who have interacted with the bot:\n{user_names_list}")
    else:
        await update.message.reply_text(
            "You are not authorized to view this information.")


if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, search_news))
    application.add_handler(
        CommandHandler("usernames", get_usernames)
    )  # Nouvelle commande pour afficher les usernames des utilisateurs

    # Run the bot
    application.run_polling()
