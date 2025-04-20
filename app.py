from flask import Flask, request, jsonify
import logging
import json
import threading
from handle_message import main_no_async
from apscheduler.schedulers.background import BackgroundScheduler
from models import User , Advertise
from database import AsyncSession as DBSession
from datetime import datetime, timedelta
from sqlalchemy.future import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import asyncio
app = Flask(__name__)


@app.route('/', methods=['GET'])
def successfully_connection():
    print("Connection Is Ok")
    return webhook


@app.route('/auth', methods=['GET'])
def auth():
    logging.info("----------Auth = " + str(request.args))
    return "Ok", 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        hub_mode = request.args.get('hub.mode')
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')

        if hub_verify_token == 'AmirAtomAmirAtomAmirAtom@@':
            return hub_challenge
        return 'Verification token mismatch', 403

    elif request.method == 'POST':
        try:
            data = json.loads(request.data.decode('utf-8'))

            try:
                if data['entry'][0]['messaging'][0]['message']['is_echo']:
                    return 'Success', 200
            except KeyError:
                pass

            message_text = data['entry'][0]['messaging'][0]['message']['text']
            sender_id = data['entry'][0]['messaging'][0]['sender']['id']
            logging.info(str(data))

            if data['entry'][0]['id'] == '17841469553848219':
                try:
                    if data['entry'][0]['messaging'][0]['message']['reply_to']['story']:
                        id_story = data['entry'][0]['messaging'][0]['message']['reply_to']['story']['id']
                        threading.Thread(target=main_no_async, args=(sender_id, message_text, True, id_story)).start()
                        return 'Success', 200
                except KeyError:
                    threading.Thread(target=main_no_async, args=(sender_id, message_text, False)).start()
                    return 'Success', 200

            else:
                pass
                # try:
                #     if data['entry'][0]['messaging'][0]['message']['reply_to']['story']:
                #         id_story = data['entry'][0]['messaging'][0]['message']['reply_to']['story']['id']
                #         threading.Thread(target=test_no_async, args=(sender_id, message_text, True, id_story)).start()
                #         return 'Success', 200
                # except KeyError:
                #     threading.Thread(target=test_no_async, args=(sender_id, message_text, False)).start()
                #     return 'Success', 200

        except Exception as e:
            logging.error(str(e))
            return jsonify({"Error": str(e)}), 500

    return 'Invalid method', 405



async def reset_usage():
    async with DBSession() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            user.usage = 0
        await session.commit()
        print("✅ usage reset for all users.")

async def cleanup_advertises():
    async with DBSession() as session:
        async with session.begin():
            now = datetime.utcnow()
            threshold = now - timedelta(days=7)

            result = await session.execute(
                select(Advertise).where(
                    Advertise.status == True,
                    Advertise.show == True,
                    Advertise.show_at != None,
                    Advertise.show_at < threshold
                )
            )
            to_delete = result.scalars().all()
            count_to_replace = len(to_delete)

            for ad in to_delete:
                await session.delete(ad)

            if count_to_replace > 0:
                result = await session.execute(
                    select(Advertise).where(
                        Advertise.status == True,
                        Advertise.show == False
                    ).order_by(Advertise.accept_at.asc()).limit(count_to_replace)
                )
                replacements = result.scalars().all()
                for ad in replacements:
                    ad.show = True
                    ad.show_at = datetime.utcnow()

            await session.commit()
            print(f"✅ {len(to_delete)} ads deleted, {len(replacements)} ads activated.")

def run_async_job():
    asyncio.run(midnight_tasks())

async def midnight_tasks():
    await reset_usage()
    await cleanup_advertises()
    print("🌙 Midnight tasks completed.")

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Tehran"))
    scheduler.add_job(run_async_job, CronTrigger(hour=0, minute=0))
    scheduler.start()
    print("⏰ Midnight job scheduled.")

if __name__ == '__main__':
    start_scheduler()
    app.run()
