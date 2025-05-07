from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton, Document
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, Application
)

application = Application.builder().token(TOKEN).build()

# Estados da conversa
(
    NOME, TIPO_PROPOSTA, TIPO_PLANO, OPERADORA,
    ANEXOS, FINALIZAR
) = range(6)

# Operadoras (simplificadas aqui por espaço, mas você pode colar a lista completa)
OPERADORAS = [
    "Bradesco", "Amil", "GNDI", "Prevent Senior", "Ampla PME",
    "Unimed nacional", "Sulamérica", "Supermed", "All Care", "Omint", "Sami", "CNU"
    # Adicione todas que você listou
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bem-vindo ao portal do setor de Implantações.\n\nPor favor, informe seu *nome completo*:",
        parse_mode="Markdown"
    )
    return NOME

async def get_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nome"] = update.message.text
    keyboard = [["PME", "PF", "Adesão"]]
    await update.message.reply_text(
        "Qual o tipo de proposta?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return TIPO_PROPOSTA

async def get_tipo_proposta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tipo_proposta"] = update.message.text
    keyboard = [["Saúde", "Odonto"]]
    await update.message.reply_text(
        "Qual o tipo de plano?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return TIPO_PLANO

async def get_tipo_plano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tipo_plano"] = update.message.text

    # Divide a lista em blocos de 3 para o teclado
    operadora_botoes = [OPERADORAS[i:i + 3] for i in range(0, len(OPERADORAS), 3)]
    await update.message.reply_text(
        "Qual a operadora?",
        reply_markup=ReplyKeyboardMarkup(operadora_botoes, one_time_keyboard=True, resize_keyboard=True)
    )
    return OPERADORA

async def get_operadora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["operadora"] = update.message.text

    await update.message.reply_text(
        "Por favor, envie os seguintes documentos:\n\n"
        "📎 Cotação do plano\n"
        "📎 Documentos da empresa: CNPJ, Contrato Social, FGTS, documento do sócio\n"
        "📎 Documentos dos beneficiários: RG/CPF, SUS, contato, comprovante de endereço, etc.\n"
        "📎 Caso PJ: CNPJ, contrato social, prestação de serviço\n"
        "📎 Caso plano anterior: carteirinha, carta permanência, boletos\n\n"
        "Você pode enviar todos os arquivos agora (PDF, JPEG, DOC...). Quando terminar, envie a mensagem *finalizar*.",
        parse_mode="Markdown"
    )
    context.user_data["anexos"] = []
    return ANEXOS

async def get_anexos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        file_info = update.message.document
        context.user_data["anexos"].append(file_info.file_name)
        await update.message.reply_text(f"📁 Recebido: {file_info.file_name}")
    elif update.message.text.lower() == "finalizar":
        return await finalizar(update, context)
    else:
        await update.message.reply_text("Por favor, envie o arquivo como anexo ou digite *finalizar* para encerrar.")
    return ANEXOS

async def finalizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = context.user_data
    resumo = (
        f"✅ *Dados recebidos:*\n\n"
        f"👤 Corretor: {dados['nome']}\n"
        f"📄 Tipo de proposta: {dados['tipo_proposta']}\n"
        f"🩺 Tipo de plano: {dados['tipo_plano']}\n"
        f"🏥 Operadora: {dados['operadora']}\n"
        f"📎 Anexos: {len(dados['anexos'])} arquivos\n"
    )
    await update.message.reply_text(resumo, parse_mode="Markdown")

    # Aqui você pode enviar por e-mail, salvar no banco etc.
    await update.message.reply_text(
        "As informações foram enviadas ao setor responsável. O que deseja fazer agora?",
        reply_markup=ReplyKeyboardMarkup([["Enviar nova cotação", "Encerrar"]], one_time_keyboard=True)
    )
    return FINALIZAR

async def encerrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Enviar nova cotação":
        return await start(update, context)
    else:
        await update.message.reply_text("✅ Atendimento encerrado. Obrigado!")
        return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operação cancelada.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nome)],
            TIPO_PROPOSTA: [MessageHandler(filters.TEXT, get_tipo_proposta)],
            TIPO_PLANO: [MessageHandler(filters.TEXT, get_tipo_plano)],
            OPERADORA: [MessageHandler(filters.TEXT, get_operadora)],
            ANEXOS: [MessageHandler(filters.Document.ALL | filters.TEXT, get_anexos)],
            FINALIZAR: [MessageHandler(filters.TEXT, encerrar)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv)
    print("Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()