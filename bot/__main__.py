from telegram.ext import CommandHandler, run_async
from bot.gDrive import GoogleDriveHelper
from bot.fs_utils import get_readable_file_size
from bot import LOGGER, dispatcher, updater, bot
from bot.config import BOT_TOKEN, OWNER_ID, GDRIVE_FOLDER_ID
from bot.decorators import is_authorised, is_owner
from telegram.error import TimedOut, BadRequest
from bot.clone_status import CloneStatus
from bot.msg_utils import deleteMessage, sendMessage
import time

REPO_LINK = "https://github.com/jagrit007/Telegram-CloneBot"
# Soon to be used for direct updates from within the bot.

@run_async
def start(update, context):
    sendMessage("**စတင်သုံးနိုင်ပါပြီ။ သိရှိလိုသောအချက်ရှိလျှင် @drivetalk group တွင် မေးမြန်းနိုင်ပါတယ်။**" \
        "\n/help နှိပ်ပြီး အသုံးပြုနည်း လေ့လာပါ။",
    context.bot, update, 'Markdown')
    # ;-;

@run_async
def helper(update, context):
    sendMessage("SA သုံးပါက Source Drive နှင့် ကူးမည့်မိမိShareDrive တိုတွင် group mail ကို contributor အဖြစ် add ထားမှ ကူးလိုရမှာပါ။ addနည်းကို ဒီမှာကြည့်ပါ။https://tiny.one/dwtykxca\n\n" \
        "*ကူးယူပုံမှာ* `/clone SourceLink DentinationFolderLink`\n*အရေးကြီးသတိပြုရန်* \n1. `/clone နောက်မှာ၁ခါ sourceLinkနောက်မှာတခါ *Space* ပါပါတယ်`\n2. `အဲ့ဒီလိုမဟုတ်ရင်code က အလုပ်လုပ်မည်မဟုတ်ပါ`" \
            "\nအဆင်ပြေကြမယ်လို့ထင်ပါတယ်။" \
            "\n\nservice accountတွေ ထည့်ထားလျှင် ဒေတာ Tb နဲ့ချီ ကူးလို့ရပါတယ်။\n" \
                "`ထိုသို့ကူးနိုင်သည်မှာမှန်သော်လည်း`\nတစ်ရက်ထဲ အများကြိးကူးလိုက်ရင် limit ပြည့်သွားပါမယ်။" \
                    "*ဒါကြောင့် တစ်ရက်ကို maximun 10-20Tb/day လောက်ပဲကူးသင့်ပါတယ်။*\n" \
                        f"Source of this bot: [GitHub]({REPO_LINK})", context.bot, update, 'Markdown')

# TODO Cancel Clones with /cancel command.
@run_async
@is_authorised
def cloneNode(update, context):
    args = update.message.text.split(" ")
    if len(args) > 1:
        link = args[1]
        try:
            ignoreList = args[-1].split(',')
        except IndexError:
            ignoreList = []

        DESTINATION_ID = GDRIVE_FOLDER_ID
        try:
            DESTINATION_ID = args[2]
            print(DESTINATION_ID)
        except IndexError:
            pass
            # Usage: /clone <FolderToClone> <Destination> <IDtoIgnoreFromClone>,<IDtoIgnoreFromClone>

        msg = sendMessage(f"<b>Cloning:</b> <code>{link}</code>", context.bot, update)
        status_class = CloneStatus()
        gd = GoogleDriveHelper(GFolder_ID=DESTINATION_ID)
        sendCloneStatus(update, context, status_class, msg, link)
        result = gd.clone(link, status_class, ignoreList=ignoreList)
        deleteMessage(context.bot, msg)
        status_class.set_status(True)
        sendMessage(result, context.bot, update)
    else:
        sendMessage("Please Provide a Google Drive Shared Link to Clone.", bot, update)


@run_async
def sendCloneStatus(update, context, status, msg, link):
    old_text = ''
    while not status.done():
        sleeper(3)
        try:
            text=f'⚜ *Origin* {status.MainFolderName}\n♦♦♦♦♦♦♦♦♦♦♦♦♦\n🗃️ *NowCloning* `{status.get_name()}`\n⏳ *Pass*: `{status.get_size()}`\n📁 *YourFolder* {status.DestinationFolderName}\n---❤▪▪▪▪▪▪▪❤---'
            if status.checkFileStatus():
                text += f"\n‼ *ရှိပြီးသားဖိုင်များကိုစစ်ဆေးခြင်း:* `{str(status.checkFileStatus())}`"
            if not text == old_text:
                msg.edit_text(text=text, parse_mode="Markdown", timeout=200)
                old_text = text
        except Exception as e:
            LOGGER.error(e)
            if str(e) == "Message to edit not found":
                break
            sleeper(2)
            continue
    return

def sleeper(value, enabled=True):
    time.sleep(int(value))
    return

@run_async
@is_owner
def sendLogs(update, context):
    with open('log.txt', 'rb') as f:
        bot.send_document(document=f, filename=f.name,
                        reply_to_message_id=update.message.message_id,
                        chat_id=update.message.chat_id)

def main():
    LOGGER.info("Bot Started!")
    clone_handler = CommandHandler('clone', cloneNode)
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', helper)
    log_handler = CommandHandler('logs', sendLogs)
    dispatcher.add_handler(log_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(clone_handler)
    dispatcher.add_handler(help_handler)
    updater.start_polling()

main()
