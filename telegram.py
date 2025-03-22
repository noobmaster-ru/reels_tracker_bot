from dotenv import load_dotenv
import os

from urllib.parse import urlparse

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram_dialog.widgets.input import TextInput
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ContentType, FSInputFile

from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window
)
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, List, Format, Case

from features import add_integration, get_statistics_in_excel, get_integrations

load_dotenv()

class MainMenuDialogStates(StatesGroup):
    MAIN_MENU = State()

class AddIntegrationDialogStates(StatesGroup):
    INPUT_ARTICLE = State()
    INPUT_VIDEO_URL = State()

class IntegrationsListDialogStates(StatesGroup):
    INTEGRATIONS_LIST = State()

async def to_add_integration_dialog(callback, message, dialog_manager):
    await dialog_manager.start(AddIntegrationDialogStates.INPUT_ARTICLE, mode=StartMode.RESET_STACK)

async def to_integrations_list_dialog(callback, message, dialog_manager):
    await dialog_manager.start(IntegrationsListDialogStates.INTEGRATIONS_LIST, mode=StartMode.RESET_STACK)

main_menu_dialog = Dialog(
    Window(
        Const("Главное меню"),
        Button(
            Const("Добавить интеграцию"),
            id="add_integration_button",
            on_click=to_add_integration_dialog
        ),
        Button(
            Const("Список интеграций"),
            id="integrations_list_button",
            on_click=to_integrations_list_dialog
        ),
        state=MainMenuDialogStates.MAIN_MENU
    )
)

async def on_input_article(message, source, dialog_manager, *args):
    dialog_manager.dialog_data["article"] = message.text

    await dialog_manager.next()

async def on_input_video_url(message, source, dialog_manager, *args):
    video_url = message.text
    video_url_object = urlparse(video_url)

    if video_url_object.scheme == "" or video_url_object.netloc == "":
        await message.answer("Нужно предоставить ссылку на видео")
        return
    
    try:
        if (video_url_object.netloc == "tiktok.com" or video_url_object.netloc == "www.tiktok.com") and video_url_object.path.split("/")[1].startswith("@") and video_url_object.path.split("/")[2] == "video" and len(video_url_object.path.split("/")[3]) > 0:
            service = "tiktok"
        elif (video_url_object.netloc == "youtube.com" or video_url_object.netloc == "www.youtube.com") and video_url_object.path.split("/")[1] == "shorts" and len(video_url_object.path.split("/")[2]) > 0:
            service = "youtube"
        elif (video_url_object.netloc == "vk.com" or video_url_object.netloc == "www.vk.com") and video_url_object.path[1:].split("-")[0] == "clips" and len(video_url_object.path[1:].split("-")[1]) > 0 and video_url_object.query.split("=")[0] == "z" and video_url_object.query.split("=")[1].split("-")[0] == "clip" and len(video_url_object.query.split("=")[1].split("-")[1].split("_")[0]) > 0 and len(video_url_object.query.split("=")[1].split("-")[1].split("_")[1]) > 0:
            service = "vk"
        elif (video_url_object.netloc == "instagram.com" or video_url_object.netloc == "www.instagram.com") and ((len(video_url_object.path.split("/")[1]) > 0 and video_url_object.path.split("/")[2] == "reel" and len(video_url_object.path.split("/")[3]) > 0) or ((video_url_object.path.split("/")[1] == "reel" or video_url_object.path.split("/")[1] == "reels") and len(video_url_object.path.split("/")[2]) > 0)):
            service = "instagram"
        else:
            await message.answer("Вы предоставили ссылку неверного формата")
            return
    except:
        await message.answer("Вы предоставили ссылку неверного формата")
        return

    if await add_integration(
        str(message.from_user.id),
        dialog_manager.dialog_data["article"],
        service,
        video_url
    ) == "EXIST":
        await message.answer("Интеграция для этого ролика уже есть")
        await dialog_manager.start(MainMenuDialogStates.MAIN_MENU, mode=StartMode.RESET_STACK)
    else:
        await message.answer("Интеграция добавлена успешно")
        await dialog_manager.start(MainMenuDialogStates.MAIN_MENU, mode=StartMode.RESET_STACK)

add_integration_dialog = Dialog(
    Window(
        Const("Введите артикль: "),
        TextInput(
            id="article_input",
            on_success=on_input_article,
            type_factory=str
        ),
        state=AddIntegrationDialogStates.INPUT_ARTICLE
    ),
    Window(
        Const("Введите ссылку на видео: "),
        TextInput(
            id="video_url_input",
            type_factory=str,
            on_success=on_input_video_url
        ),
        state=AddIntegrationDialogStates.INPUT_VIDEO_URL
    )
)

async def get_data_for_integrations_list(**kwargs):
    telegram_user_id = kwargs["event_context"].user.id

    integrations = get_integrations(str(telegram_user_id))
    
    return {
        "integrations": integrations
    }

def integrations_list_is_empty(data, case, dialog_manager):
    return len(data["integrations"]) == 0

integrations_list_dialog = Dialog(
    Window(
        Case(
            {
                True: Const("У вас нет интеграций"),
                False: List(
                    Format(
                        "Артикул: {item[article]}\nСервис: {item[service]}\nСсылка на видео: {item[link]}\nПолучить статистику в Excel - https://t.me/Testdolbaebob_bot?start=get_statistics-{item[id]}\n\n"
                    ),
                    items="integrations"
                ),
            },
            selector=integrations_list_is_empty
        ),
        getter=get_data_for_integrations_list,
        state=IntegrationsListDialogStates.INTEGRATIONS_LIST
    )
)

storage = MemoryStorage()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

dp = Dispatcher(storage=storage)

dp.include_router(main_menu_dialog)
dp.include_router(add_integration_dialog)
dp.include_router(integrations_list_dialog)

setup_dialogs(dp)

@dp.message(Command("start"))
async def start(message, dialog_manager, command):
    if command.args != None:
        if command.args.startswith("get_statistics"):
            integration_id = int(command.args.split("-")[1])
            excel_filename = get_statistics_in_excel(integration_id)

            await message.answer_document(FSInputFile(excel_filename))
    else:
        await dialog_manager.start(MainMenuDialogStates.MAIN_MENU, mode=StartMode.RESET_STACK)

@dp.message(Command("get_statistics"))
async def get_statistics(message: Message, dialog_manager, command):
    integration_id = int(command.args)
    excel_filename = get_statistics_in_excel(integration_id)

    await message.answer_document(FSInputFile(excel_filename))

def main():
    dp.run_polling(bot, skip_updates=True)
