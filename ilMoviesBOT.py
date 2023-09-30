from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, Updater, MessageHandler, Filters, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import re
from telegram.ext import Updater, CommandHandler
import logging

warnings_count = 0
all_admins = {}
warned_Users = {}

# פונקציה שתשלח הודעת ברוך הבא עם השם המשתמש והשם האמיתי של המשתמש
def welcome(update: Update, context: CallbackContext):
    # הבוט שולח הודעה אם הגענו למספר עגול של משתמשים
    chat_id = update.message.chat_id
    new_members = update.message.new_chat_members
    total_chat_members_count = context.bot.get_chat_member_count(chat_id)
    old_total_chat_members_count = int(total_chat_members_count) - len(new_members)
    for user in new_members:
        # עבור כל אחד מהמשתמשים החדשים תשלח הודעה ברוך הבא
        user_id = user.id
        full_name = str(user.first_name) + " " + str(user.last_name) if user.last_name else str(user.first_name)
        user_ID_tag = "[" + str(full_name) + "](tg://user?id=" + str(user_id) + ")"
        chat_id = update.message.chat_id
        image_path = "dependence/images/sratim_il_new_user.jpg"  # כתבתי שהתמונה נמצאת בנתיב הזה, התאמה לפי מקום התמונה במערכת שלך
        # יצירת מערך של כפתורים
        keyboard = [[InlineKeyboardButton("כללים 📜", url='https://t.me/c/1453214668/26416')]]
        keyboard1 = [[InlineKeyboardButton("להצטרפות לערוץ הסרטים🖥️", url='https://t.me/Il_sratim_bot')]]

        reply_markup = InlineKeyboardMarkup(keyboard + keyboard1)

        chat_name = update.message.chat.title

        text_with_photo = f"היי {user_ID_tag} ברוך/ה הבא/ה ל {chat_name}\n🇮🇱💢🇮🇱💢🇮🇱💢🇮🇱💢🇮🇱💢🇮🇱"
        po = context.bot.send_photo(chat_id=chat_id, photo=open(image_path, 'rb'), reply_markup=reply_markup,
                                    caption=text_with_photo, parse_mode='Markdown')

        # הוסף משימה למחיקת ההודעה שנשלחה לאחר דקה
        context.job_queue.run_once(delete_message, 60, context=(chat_id, po.message_id))

        # בדיקה אם אחרי הוספת כל אחד מהמשתמשים הגענו למספר עגול
        old_total_chat_members_count += 1
        new_total_chat_members_count = old_total_chat_members_count
        if new_total_chat_members_count % 1000 == 0:  # בדוק אם מספר המשתמשים הוא מספר עגול של 1000
            keyboard = [[InlineKeyboardButton("לשיתוף ♻️", url='https://t.me/share/url?url=https://t.me/sratim_IL')]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            Mazel_Tov = context.bot.send_message(chat_id=chat_id,
                                                 text=f"מזל טוב הגענו ל- *{total_chat_members_count} מנויים* בקבוצה 🥳\nשתפו אותנו שנמשיך להיות הקבוצה הגדולה בטלגרם😍🦾",
                                                 parse_mode='Markdown', reply_markup=reply_markup)
            # הוסף משימה למחיקת ההודעה שנשלחה לאחר דקה
            context.job_queue.run_once(delete_message, 120, context=(chat_id, Mazel_Tov.message_id))

    # מחק את הודעת ההצטרפות האוטומטית
    update.message.delete()

# פונקציה שבודקת אם המשתמש או ההודעה מכילים אותיות בשפה בערבית או בשפה הפרסית
def contains_arabic_or_persian(text):
    arabic_letters = 'ابتثجحخدذرزسشصضطظعغفقكلمنهويآأإ'
    persian_letters = 'اٱبپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیئؤ'
    for letter in text:
        if letter in arabic_letters or letter in persian_letters:
            return True
    return False

    # פונקציה שתבדוק את התנאים ותסיר את המשתמש מהקבוצה אם התנאים מתקיימים
def Run_after_every_message_sent_in_the_group(update: Update, context: CallbackContext):
    is_edit = False
    is_reply_msg = False

    if update.edited_message:
        UpMsg = update.edited_message
        is_edit = True
    else:
        UpMsg = update.message

    if UpMsg.reply_to_message:
        is_reply_msg = True

    chat_id = UpMsg.chat_id
    msg_sender_user_msg = UpMsg
    msg_sender_user_msg_text = UpMsg.text
    original_message_id = UpMsg.message_id
    msg_sender_user_id = UpMsg.from_user.id
    msg_sender_full_name = str(UpMsg.from_user.first_name) + " " + str(
        UpMsg.from_user.last_name) if UpMsg.from_user.last_name else str(
        UpMsg.from_user.first_name)
    msg_sender_user_ID_tag = "[" + str(msg_sender_full_name) + "](tg://user?id=" + str(msg_sender_user_id) + ")"

    if is_reply_msg:
        the_warned_user_id = UpMsg.reply_to_message.from_user.id
        the_warned_user_full_name = str(UpMsg.reply_to_message.from_user.first_name) + " " + str(
            UpMsg.reply_to_message.from_user.last_name) if UpMsg.reply_to_message.from_user.last_name else str(
            UpMsg.reply_to_message.from_user.first_name)
        the_warned_user_ID_tag = "[" + str(the_warned_user_full_name) + "](tg://user?id=" + str(the_warned_user_id) + ")"

    chat_admins = context.bot.get_chat_administrators(chat_id)

    all_admins = {}
    # עבור על רשימת המנהלים והדפס את מזהה כל אחד מהם
    for admin in chat_admins:
        # השגת מזהה המנהל
        admin_id = admin.user.id
        # השגת השם המלא של המנהל
        admin_details = context.bot.get_chat(admin_id)
        full_admin_name = str(admin_details.first_name) + " " + str(admin_details.last_name) if admin_details.last_name else str(
            admin_details.first_name)
        # אחסון המנהל בתוך מילון המנהלים
        all_admins[full_admin_name] = admin_id

    # ניקוי אזהרות מהמנהלים
    for admin in all_admins.values():
        warned_Users[admin] = f"{0}"

# כאן נבדוק אם ההודעה היא בערבית או פרסית ונמשיך בהתאם
    if contains_arabic_or_persian(msg_sender_user_msg_text) or contains_arabic_or_persian(msg_sender_full_name):

        if not msg_sender_user_id in all_admins.values():
            # שלח הודעה למשתמש שהתנהל מהקבוצה
            sent_message = UpMsg.reply_text(
                f"{msg_sender_user_ID_tag}, הודעתך נמחקה משום שהיא מכילה אותיות בשפה בערבית או בשפה הפרסית. המשתמש נורשה מהקבוצה.", parse_mode='Markdown')
            # הסר את המשתמש מהקבוצה
            context.bot.ban_chat_member(UpMsg.chat_id, msg_sender_user_id)

            # מחק את ההודעה המכילה את המילים בערבית או פרסית גם מהשולח
            context.bot.delete_message(UpMsg.chat_id, original_message_id)

            # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
            context.job_queue.run_once(delete_message, 60, context=(UpMsg.chat_id, sent_message.message_id))

# כאן נבדוק אם משתמש שלח קישור
    link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    word_to_remove = [
        "https://t.me/sratim_IL"
    ]
    old_user_msg = msg_sender_user_msg_text
    for word in word_to_remove:
        msg_sender_user_msg_text = msg_sender_user_msg_text.replace(word, '')

    # בדיקה האם יש קישור בטקסט
    if re.search(link_pattern, msg_sender_user_msg_text):
        warning_reason = "שליחת קישור"
        # בירור אם שולח הקישור אינו מנהל
        if not msg_sender_user_id in all_admins.values():
            # אזהרת השולח
            if not msg_sender_user_id in warned_Users:
                warned_Users[msg_sender_user_id] = 0
            warned_Users[msg_sender_user_id] = f"{int(warned_Users[msg_sender_user_id]) + 1}"
            if int(warned_Users[msg_sender_user_id]) >= 3:
                warned_Users[msg_sender_user_id] = 0
                # שלח הודעה כי המשתמש קיבל 3 אזהרות והוא נמחק מהקבוצה
                Removal_message = UpMsg.reply_text(f"משתמש {msg_sender_user_ID_tag} הגיע למגבלה של האזהרות והועף מהקבוצה.", parse_mode='Markdown')
                context.bot.ban_chat_member(chat_id, msg_sender_user_id)
                # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                context.job_queue.run_once(delete_message, 60,
                                           context=(chat_id, Removal_message.message_id))
            else:
                amount_warnings_msg = UpMsg.reply_text(
                    f"משתמש {msg_sender_user_ID_tag} קיבל *אזהרה ({warned_Users[msg_sender_user_id]}/3)*,\n*סיבה:* {warning_reason}", parse_mode='Markdown')
                # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                context.job_queue.run_once(delete_message, 60,
                                           context=(chat_id, amount_warnings_msg.message_id))

            # מחיקת הקישור שניה אחת אחרי הגעתו
            context.job_queue.run_once(delete_message, 1,
                                       context=(chat_id, original_message_id))

# כאן נבדוק אם מנהל הזהיר משתמש
    if is_reply_msg:
        # קביעת משתנה להכיל את המזהה של המשתמש המוזהר
        words = msg_sender_user_msg_text.split(' ', # פצל את ההודעה למילים
                           1)  # הפרמטר 1 מציין שנרצה לחלק את הטקסט ל־2 חלקים רק, כאשר המילה הראשונה תהיה במשתנה הראשון
        if len(words) == 2:
            first_word = words[0]
            rest_of_text = words[1]
        else:
            first_word = msg_sender_user_msg_text  # אם אין רווחים בטקסט, המילה היא הטקסט כולו
            rest_of_text = "לא צוינה"
        if first_word == "/הזהר":  # בדוק אם ההודעה מתחילה ב"/הזהר"
            if not is_edit:
                # האם המשתמש המזהיר הינו ברשימת המנהלים
                if msg_sender_user_id in all_admins.values():
                    if not the_warned_user_id in all_admins.values():
                        warning_reason = rest_of_text
                        if not the_warned_user_id in warned_Users:
                            warned_Users[the_warned_user_id] = 0
                        warned_Users[the_warned_user_id] = f"{int(warned_Users[the_warned_user_id]) + 1}"
                        if int(warned_Users[the_warned_user_id]) >= 3:
                            # שלח הודעה כי המשתמש קיבל 3 אזהרות והוא נמחק מהקבוצה
                            warned_Users[the_warned_user_id] = 0
                            Removal_message = UpMsg.reply_text(f"משתמש {the_warned_user_ID_tag} הגיע למגבלה של האזהרות והועף מהקבוצה.", parse_mode='Markdown')
                            context.bot.ban_chat_member(chat_id, the_warned_user_id)
                            # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                            context.job_queue.run_once(delete_message, 60,
                                                       context=(chat_id, Removal_message.message_id))
                        else:
                            amount_warnings_msg = UpMsg.reply_text(
                                f"משתמש {the_warned_user_ID_tag} קיבל *אזהרה ({warned_Users[the_warned_user_id]}/3)*,\n*סיבה:* {warning_reason}", parse_mode='Markdown')
                            # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                            context.job_queue.run_once(delete_message, 60,
                                                       context=(chat_id, amount_warnings_msg.message_id))
                    else:
                        cant_warn_manager_message = UpMsg.reply_text(f"לא ניתן להזהיר מנהל")
                        # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                        context.job_queue.run_once(delete_message, 60,
                                                   context=(chat_id, cant_warn_manager_message.message_id))
                else:
                    manager_command_only_message = UpMsg.reply_text(f"פקודה זאת רק למנהלים")
                    # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                    context.job_queue.run_once(delete_message, 60,
                                               context=(chat_id, manager_command_only_message.message_id))

            else:
                cant_deal_with_edited_messages = UpMsg.reply_text(f"אי אפשר להזהיר עם הודעות ערוכות (הודעתך תמחק)")
                # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                context.job_queue.run_once(delete_message, 60,
                                           context=(chat_id, cant_deal_with_edited_messages.message_id))

            # מחיקת ההודעה אחרי דקה /הזהר אפילו אם השולח אינו מנהל
            context.job_queue.run_once(delete_message, 60, context=(chat_id, original_message_id))


        if msg_sender_user_msg_text == "/נקה אזהרות":  # בדוק אם ההודעה מתחילה ב"/נקה אזהרות"
            if not is_edit:
                if msg_sender_user_id in all_admins.values():
                    if not the_warned_user_id in all_admins.values():
                        if not the_warned_user_id in warned_Users:
                            warned_Users[the_warned_user_id] = 0
                        warned_Users[the_warned_user_id] = f"{0}"
                        amount_warnings_msg = update.message.reply_text(
                                f"למשתמש {the_warned_user_ID_tag} יש עכשיו *({warned_Users[the_warned_user_id]}/3) אזהרות*!", parse_mode='Markdown')
                        # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                        context.job_queue.run_once(delete_message, 60,
                                                   context=(chat_id, amount_warnings_msg.message_id))
                    else:
                        cant_warn_manager_message = UpMsg.reply_text(f"אין צורך לנקות אזהרות למנהלים")
                        # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                        context.job_queue.run_once(delete_message, 60,
                                                   context=(chat_id, cant_warn_manager_message.message_id))
                else:
                    manager_command_only_message = update.message.reply_text(f"פקודה זאת רק למנהלים")
                    # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                    context.job_queue.run_once(delete_message, 60,
                                               context=(chat_id, manager_command_only_message.message_id))

            else:
                cant_deal_with_edited_messages = UpMsg.reply_text(f"אי אפשר לנקות אזהרות עם הודעות ערוכות (הודעתך תמחק)")
                # הוסף משימה למחיקת ההודעה שנשלחה למשתמש אחרי דקה
                context.job_queue.run_once(delete_message, 60,
                                           context=(chat_id, cant_deal_with_edited_messages.message_id))

            # מחיקת ההודעה אחרי דקה /הזהר אפילו אם השולח אינו מנהל
            context.job_queue.run_once(delete_message, 60, context=(chat_id, original_message_id))

def delete_message(context: CallbackContext):
    chat_id, message_id = context.job.context
    context.bot.delete_message(chat_id, message_id)

# פונקציה לטיפול בהודעות יציאה מהקבוצה
def handle_left_chat_member(update, context):
    # מחק את הודעת היציאה
    update.message.delete()

def main():
    # רישום לוגים
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # טוקן של הבוט שלך
    bot_token = "6366187381:AAGXCLN0b5YOXwWys85CJNVAWlH9Ct3BmGk"

    # יצירת אפליקציה והוספת פקודות וטיפול בהודעות
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue  # הוספת קרונים לטיפול במשימות מאוחרות

    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))

    # הוסף את הטיפול בפקודה "/הזהר" לפקודות שמתעסקות בהודעות
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.chat_type.groups, Run_after_every_message_sent_in_the_group, edited_updates=Update.EDITED_MESSAGE))

    # הוסף פונקציה לטיפול בהודעות יציאה
    dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, handle_left_chat_member))


    # התחלת הבוט
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()