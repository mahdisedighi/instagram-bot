from sqlalchemy.util import await_only

from env import instagram_api, job_list
import requests
import logging
import asyncio
from database import *
import re
from generate_message import ProcessText
from read_files import r , sr , limit
from env import has_limit

HEADER = {
    "Authorization": "Bearer " + instagram_api,
    "Content-Type": "application/json"
}

Base_URL = "https://graph.instagram.com/v21.0/"

async def SendInstaMessage(sender, msg):
    logging.info("------------|| Send To" + str(sender) + " : " + str(msg))
    data = {
        'recipient': {'id': sender},
        'message': {'text': msg}
    }

    re = requests.post(f"{Base_URL}me/messages", headers=HEADER, json=data)

    if re.status_code == 200:
        return True

    logging.error(str(re.status_code))
    logging.error(str(re.text))
    return False



data_messages = {}

async def Main(sender_id, message_text , status_story = False , id_story =None):
    logging.info("In Thread")

    user_exist = await user_exists(sender_id)
    response = requests.get(f'{Base_URL}{sender_id}', headers=HEADER).json()
    username = response['username']

    # if user is not in database

    if not user_exist:
        user = await register_user(sender_id)

        await update_user_username(user , username)
        data_messages[sender_id] = [
            {"role": "system", "content": r},
            {'role': 'assistant', 'content': 'اوکي'}
        ]

        logging.info("Register User")

    # if user is in database
    else:
        user = await get_user(sender_id)
        if "%getjob%" in message_text:
            number_job = message_text.replace("%getjob%","")
            try:
                number_job = int(number_job.strip())
            except:
                msg = "فرمت ارسالی مورد قبول نیست!!!"
                await SendInstaMessage(sender_id ,msg)
                return


            job_name = job_list[number_job-1]

            result_job = await get_advertise(ad_name=job_name)
            if result_job:
                msg = f"""
                موارد یافت شده برای {job_name} :
                
                """
                count = 0
                for item in result_job:
                    msg += f"""
                    {count+1} : @{item.username}
                    توضیحات : {item.description}
                    
                    """
            else:
                await SendInstaMessage(sender_id , "موردی یافت نشد!!!")

            return


        if "%acceptjob%" in message_text:
            text_accept = message_text.replace("%acceptjob%")
            text_accept = text_accept.stirp()
            user_id = text_accept.repalce(" " ,"")
            status_ad = await status_advertise(user_id)
            if status_ad.status:
                await SendInstaMessage("1276925199997737" , "قبلا تایید شده!!")
            else:
                await acceppt_advertise(status_ad)
                await SendInstaMessage(user_id , "آیدی شما توسط ادمین تایید شد")
                await SendInstaMessage("1276925199997737" , "تایید شده!!")

            return


        if "%job%" in message_text:
            text_job = message_text.replace("%job%","")
            if "عنوان" or "توضیحات" not in text_job:
                await SendInstaMessage(sender_id , "فرمت ارسالی مورد قبول نیست!!")
                text_format ='''
                %addjob%
                عنوان : ...
                توضیحات : ...
                '''
                await SendInstaMessage(sender_id , text_format)
                return

            else:
                text_job = message_text.split('توضیحات')
                title = text_job[0].replace("عنوان" , "").replace(":" ,"").strip()
                title = title.strip()

                description = text_job[1].replace('توضیحات' ,"").replace(':' , "").strip()
                description = description.strip()
                if title not in job_list:
                    await SendInstaMessage(sender_id , "شغل مورد پذیرش نیست!!!")
                    return


                if not await advertise_exist(user):
                    await add_advertise(user ,username ,title ,description)
                    await SendInstaMessage(sender_id ,"ذخيره شد!!")
                    await SendInstaMessage("1276925199997737" , f'@{username}')
                else:
                    await SendInstaMessage(sender_id , "این یوزرنیم قبلا ثبت شده")

                return






        if "%من%" in message_text:
            message_custom = message_text.replace('%من%' ,'')
            await update_text_custom(user , message_custom)
            await SendInstaMessage(sender_id , "ثبت شد.\nحالا بهتر میشناسمت!")
            return




        if status_story == True:
            mes_story = await get_text_story(int(id_story))

            if ("edit" in message_text) and mes_story:
                if sender_id == "1276925199997737":
                    message_text = re.sub(r'%[^%]+%', '', message_text)

                    xxx = re.sub(r'\bedit\b', '', message_text, flags=re.IGNORECASE)
                    mes_story.text = xxx.strip()
                    await sync_to_async(mes_story.save)()
                    await SendInstaMessage("1276925199997737", "ذخيره شد!!")

                    return

            if mes_story == False:
                txt = re.search(r'%([^%]+)%', message_text)
                if txt:
                    if sender_id == "1276925199997737":
                        mes_story = re.sub(r'%[^%]+%', '', message_text)
                        await add_text_story(int(txt.group(1)), mes_story.strip())
                        await SendInstaMessage("1276925199997737", "ذخيره شد!!")
                else:
                    # this is just for admin 395620980214729
                    if sender_id == "1276925199997737":
                        await SendInstaMessage("1276925199997737", id_story)
                return

            mes_story = f"خدوتو در این موقعیت قرار بده و با توجه به اون پاسخ بده : {mes_story.text}"

        if sender_id in data_messages:
            if status_story == True:
                data_messages[sender_id].append({'role': 'system', 'content': mes_story})
                data_messages[sender_id].append({'role': 'user', 'content': message_text})

            else:
                data_messages[sender_id].append({'role': 'user', 'content': message_text})
        else:
            latest_messages = await last_message(user)
            text_coustom = user.text_custom
            if text_coustom is not None:
                content_text_coustom = f"""اطلاعاتی که میتونم راجع به کابر بهت بدم اینه باید توی پردازش هایی که انجام میدی اینو هم مد نظرت بگیری {text_coustom}"""
                data_messages[sender_id] = [
                    {"role": "system", "content": r},
                    {"role": "system", "content": content_text_coustom},
                    {'role': 'assistant', 'content': 'اوکي'},]

            else:
                data_messages[sender_id] = [
                    {"role": "system", "content": r},
                    {'role': 'assistant', 'content': 'اوکي'}, ]

            for mesa in latest_messages:
                if mesa.is_user:
                    data_messages[sender_id].append({'role': 'user', "content": mesa.content})
                else:
                    data_messages[sender_id].append({'role': 'assistant', 'content': mesa.content})

            if status_story == True:
                data_messages[sender_id].append({'role': 'system', 'content': mes_story})
                data_messages[sender_id].append({'role': 'user', 'content': message_text})
            else:
                data_messages[sender_id].append({'role': 'user', 'content': message_text})


    # check if bot has limit
    if has_limit == True:
        if user.usage == limit + 1:
            await SendInstaMessage(sender_id,f"""عزیز دلم بیشتر از این نمیتونم به پیام هات جواب بدم""")
            await update_user_usage(user)
            return
        elif user.usage > limit + 1:
            await SendInstaMessage(sender_id, f"""عزیز دلم بیشتر از این نمیتونم به پیام هات جواب بدم
                                                اگه میخوام دوباره باهام صحبت کنی باید صبر بدی تا ساعت 12 شب که محدودیتت ریست بشه و بتونی باز باهام صحبت کنی""")
            await update_user_usage(user)
            return

    await update_user_usage(user)
    username = response['username']
    user.username = username
    await sync_to_async(user.save)(using='default')

    if len(data_messages[sender_id]) == 23:
        data_messages[sender_id].pop(3)
        data_messages[sender_id].pop(3)

    if status_story == True:
        story_data_messages = {}
        text_coustom = user.text_custom
        if text_coustom is not None:
            content_text_coustom = f"""اطلاعاتی که میتونم راجع به کابر بهت بدم اینه باید توی پردازش هایی که انجام میدی اینو هم مد نظرت بگیری {text_coustom}"""
            story_data_messages[sender_id] = [
                {"role": "system", "content": sr},
                {"role": "system", "content": content_text_coustom},
                {'role': 'assistant', 'content': 'اوکي'},
                {'role': "system", "content": mes_story}

            ]
        else:
            story_data_messages[sender_id] = [
                {"role": "system", "content": sr},
                {'role': 'assistant', 'content': 'اوکي'},
                {'role': "system", "content": mes_story}

            ]

        story_data_messages[sender_id].append({'role': 'user', 'content': message_text})

        status, msg = await ProcessText(story_data_messages[sender_id])

    else:

        status, msg = await ProcessText(data_messages[sender_id])

    await save_message(user, message_text, "is_user")
    await save_message(user, msg, "is_bot")

    logging.info("GPT Message: " + str(msg))







    if status:
        data_messages[sender_id].append({'role': 'assistant', "content": msg})
        await SendInstaMessage(sender_id, msg)
        count_message = await get_user_message_count(user)
        msg = """"""
        count = 0
        for item in job_list:
            msg += f"{count+1} : {item}\n"
        msg += """
        '%getjob%'
        عدد شغل
        """
        if int(count_message) // 15:
            await SendInstaMessage(sender_id , msg)
    else:
        logging.error("Error In SendInsta: " + str(status))
        logging.error(str(msg))


def main_no_async(sender_id , message_text, status_story = False , id_story=None):
    asyncio.run(Main(sender_id ,message_text , status_story , id_story))

