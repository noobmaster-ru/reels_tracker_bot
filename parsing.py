import asyncio
import requests
import json

from urllib.parse import urlparse

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
}

def get_function(func):
    async def new_function(*args, **kwargs):
        excepts_count = 0

        while True:
            try:
                return func(*args, **kwargs)
            except:
                if excepts_count == 10:
                    return "ERROR"
                
                excepts_count = excepts_count + 1
                
                await asyncio.sleep(1)

    
    return new_function

def get_tiktok_video_data(url):
        response = requests.get(url, headers = headers)
        first_index = response.text.find('"stats"') + 8
        part = response.text[first_index:first_index + 500]
        result_string = part[0:part.find('}') + 1]

        result = json.loads(result_string)
        return {
            "views": result["playCount"],
            "likes": result["diggCount"],
            "comments": result["commentCount"]
        }
    

def get_youtube_video_data(url):
    response = requests.get(url, headers = headers)

    views_part = response.text[response.text.find('"viewCount"') + 13:]
    views = int(views_part[0:views_part.find('"')])

    likes_part = response.text[response.text.find('"likeCount"') + 12:]
    likes = int(likes_part[0:likes_part.find(",")])

    comments_part = response.text[response.text.find('"viewCommentsButton":{"buttonRenderer":{"isDisabled":false,"text":{"simpleText"') + 81:]
    comments = int(''.join(comments_part[0:comments_part.find('"')].split('\xa0')))

    return {
        "views": views,
        "likes": likes,
        "comments": comments
    }

def get_vk_video_data(url):
    url_object = urlparse(url)
    id = url_object.query[6:]

    response = requests.post("https://vk.com/al_video.php?act=show", headers = {
        "user-agent": headers["user-agent"],
        "referer": f"https://vk.com/clips{id.split('_')[0]}?z=clip{id}"
    }, data = f"act=show&al=1&autoplay=0&module=clips_item&screen=0&show_next=1&video={id}&webcast=0")
    
    video_data = json.loads(response.text[4:])["payload"][1][4]["mvData"]

    views = video_data["info"][10]
    likes = video_data["likes"]
    comments = video_data["commcount"]

    return {
        "views": views,
        "likes": likes,
        "comments": comments
    }

def get_instagram_video_data(url):
    url_object = urlparse(url)

    if url_object.path.split("/")[1] == "reel" or url_object.path.split("/")[1] == "reels":
        id = url_object.path.split("/")[2]
    else:
        id = url_object.path.split("/")[3]

    response = requests.post('https://www.instagram.com/graphql/query', headers = headers, data = {
        "variables": '{"shortcode":"' + id + '","fetch_tagged_user_count":null,"hoisted_comment_id":null,"hoisted_reply_id":null}',
        "doc_id": "8845758582119845"
    })
    
    video_data = json.loads(response.text)["data"]["xdt_shortcode_media"]

    views = video_data["video_view_count"]
    likes = video_data["edge_media_preview_like"]["count"]
    comments = video_data["edge_media_preview_comment"]["count"]

    print(response.text)

    return {
        "views": views,
        "likes": likes,
        "comments": comments
    }

parsers = {
    "tiktok": get_function(get_tiktok_video_data),
    "youtube": get_function(get_youtube_video_data),
    "vk": get_function(get_vk_video_data),
    "instagram": get_function(get_instagram_video_data),
}
