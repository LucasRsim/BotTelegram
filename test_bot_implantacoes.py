import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import ReplyKeyboardMarkup, KeyboardButton
from bot_implantacoes import start, get_nome, get_tipo_proposta

@pytest.mark.asyncio
async def test_start():
    # Mock do Update e Context
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    # Chamar a função
    state = await start(update, context)

    # Verificar se a mensagem foi enviada
    update.message.reply_text.assert_called_once_with(
        "👋 Bem-vindo ao portal do setor de Implantações.\n\nPor favor, informe seu *nome completo*:",
        parse_mode="Markdown"
    )
    # Verificar o estado retornado
    assert state == 0  # NOME

@pytest.mark.asyncio
async def test_get_nome():
    # Mock do Update e Context
    update = MagicMock()
    update.message.text = "Lucas Silva"
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {}

    # Chamar a função
    state = await get_nome(update, context)

    # Verificar se o nome foi armazenado
    assert context.user_data["nome"] == "Lucas Silva"

    # Criar o teclado esperado
    expected_keyboard = ReplyKeyboardMarkup(
        [["PME", "PF", "Adesão"]],
        one_time_keyboard=True
    )

    # Verificar se a mensagem foi enviada com o teclado correto
    update.message.reply_text.assert_called_once_with(
        "Qual o tipo de proposta?",
        reply_markup=expected_keyboard
    )
    # Verificar o estado retornado
    assert state == 1  # TIPO_PROPOSTA

@pytest.mark.asyncio
async def test_get_tipo_proposta():
    # Mock do Update e Context
    update = MagicMock()
    update.message.text = "PME"
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {}

    # Chamar a função
    state = await get_tipo_proposta(update, context)

    # Verificar se o tipo de proposta foi armazenado
    assert context.user_data["tipo_proposta"] == "PME"

    # Criar o teclado esperado
    expected_keyboard = ReplyKeyboardMarkup(
        [["Saúde", "Odonto"]],
        one_time_keyboard=True
    )

    # Verificar se a mensagem foi enviada com o teclado correto
    update.message.reply_text.assert_called_once_with(
        "Qual o tipo de plano?",
        reply_markup=expected_keyboard
    )
    # Verificar o estado retornado
    assert state == 2  # TIPO_PLANO