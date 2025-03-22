import datetime

import pandas as pd

from database.settings import session as database
from database.models import User, AdvertStat, AdvertStatMark

from parsing import parsers

def get_user(telegram_user_id):
    user = database.query(User).filter(User.telegram_user_id==telegram_user_id).first()

    if user == None:
        user = User(telegram_user_id=telegram_user_id)
        database.add(user)
        database.commit()
    
    return user

def add_advert_stat_mark(advert_stat_id, video_data):
    advert_stat_mark = AdvertStatMark(
        advert_stat_id=advert_stat_id,
        datetime=datetime.datetime.now(),
        views=video_data["views"],
        likes=video_data["likes"],
        comments=video_data["comments"]
    )
    database.add(advert_stat_mark)
    database.commit()

async def update_advert_stat_statistics(advert_stat_id):
    advert_stat = database.query(AdvertStat).filter(AdvertStat.id==advert_stat_id).first()

    get_video_data = parsers[advert_stat.service]
    video_data = await get_video_data(advert_stat.link)

    if video_data == "ERROR":
        print("Выслать уведомление в бот")
    else:
        add_advert_stat_mark(advert_stat.id, video_data)

async def add_integration(telegram_user_id, article, service, video_url):
    print("ADD_INTEGRATION")
    user = get_user(telegram_user_id)

    if database.query(AdvertStat).filter(AdvertStat.user_id==user.id, AdvertStat.link==video_url).first() != None:
        return "EXIST"

    get_video_data = parsers[service]
    video_data = await get_video_data(video_url)

    advert_stat = AdvertStat(
        user_id=user.id,
        article=article,
        service=service,
        link=video_url,
        active=True
    )
    database.add(advert_stat)
    database.commit()

    print("VIDEO_DATA")
    print(video_data)

    add_advert_stat_mark(advert_stat.id, video_data)

def get_all_active_advert_stats():
    advert_stats = database.query(AdvertStat).filter(AdvertStat.active==True).all()

    return advert_stats

def get_integrations(telegram_user_id):
    user = get_user(telegram_user_id)

    advert_stats = database.query(AdvertStat).filter(AdvertStat.user_id==user.id).all()
    integrations = [
        {
            "id": advert_stat.id,
            "article": advert_stat.article,
            "service": advert_stat.service,
            "link": advert_stat.link,
            "active": advert_stat.active
        } for advert_stat in advert_stats
    ]

    return integrations

def get_statistics_in_excel(advert_stat_id):
    advert_stat = database.query(AdvertStat).filter(AdvertStat.id==advert_stat_id).first()

    advert_stat_marks = database.query(AdvertStatMark).filter(AdvertStatMark.advert_stat_id==advert_stat_id).all()
    advert_stat_marks = [
        {
            "id": advert_stat_mark.id,
            "datetime": advert_stat_mark.datetime,
            "views": advert_stat_mark.views,
            "likes": advert_stat_mark.likes,
            "comments": advert_stat_mark.comments
        } for advert_stat_mark in advert_stat_marks
    ]

    dataframe = pd.DataFrame(
        {
            "datetime": [advert_stat_mark["datetime"] for advert_stat_mark in advert_stat_marks],
            "article": [advert_stat.article for advert_stat_mark in advert_stat_marks],
            "service": [advert_stat.service for advert_stat_mark in advert_stat_marks],
            "views": [advert_stat_mark["views"] for advert_stat_mark in advert_stat_marks],
            "likes": [advert_stat_mark["likes"] for advert_stat_mark in advert_stat_marks],
            "comments": [advert_stat_mark["comments"] for advert_stat_mark in advert_stat_marks]
        }
    )
    filename = f'{advert_stat_id}.xlsx'
    dataframe.to_excel(filename, index=False)

    return filename
