import os
import pandas as pd
import requests
from datetime import datetime, timedelta


class ThreadsAPI:
    USER_ID = os.environ.get("USER_ID")
    ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
    APP_SECRET = os.environ.get("APP_SECRET")

    def __init__(
        self,
        user_id=None,
        access_token=None,
        app_secret=None,
        limit=5,
        backfill_date_interval=7,
    ) -> None:
        self.user_id = user_id or self.USER_ID
        self.access_token = access_token or self.ACCESS_TOKEN
        self.app_secret = app_secret or self.APP_SECRET
        self.api_url = "https://graph.threads.net/v1.0"
        self.limit = limit
        self.backfill_date_interval = backfill_date_interval

    def get_user_bio(self):
        user_bio_list = [
            "id",
            "username",
            "threads_profile_picture_url",
            "threads_biography",
            "name",
        ]

        resp = requests.get(
            f"{self.api_url}/me",
            params={
                "fields": ",".join(user_bio_list),
                "access_token": self.access_token,
            },
        )
        return resp.json()

    def get_long_live_access_token(self):
        resp = requests.get(
            f"{self.api_url}/access_token",
            params={
                "grant_type": "th_exchange_token",
                "client_secret": self.app_secret,
                "access_token": self.access_token,
            },
        )
        # Developer needs to change environment ACCESS_TOKEN variable
        return resp.json()

    def get_threads_insights_by_id(self, thread_id: str) -> dict:
        print(f"insights for thread: {thread_id}...")
        insight_metric_list = ["views", "likes", "replies", "reposts", "quotes"]

        resp = requests.get(
            f"{self.api_url}/{thread_id}/insights",
            params={
                "metric": ",".join(insight_metric_list),
                "access_token": self.access_token,
            },
        )

        if resp.status_code != 200:
            raise Exception(resp.json())

        metric_dict = {}

        for data in resp.json().get("data", []):
            metric_dict[data.get("name")] = data.get("values")[0].get("value")
            continue
        return metric_dict

    def get_threads_conversation(self, media_id: str) -> pd.DataFrame:
        resp = requests.get(
            f"{self.api_url}/{media_id}/conversation",
            params={
                "fields": "id,permalink,username,timestamp,text",
                "threads-media-id": media_id,
                "access_token": self.access_token,
                "limit": self.limit if self.limit else 100,
            },
        )

        if resp.status_code != 200:
            raise Exception(resp.json())

        df = pd.DataFrame.from_dict(resp.json().get("data", []))

        return df

    def get_threads_df(self) -> pd.DataFrame:
        # set up params
        start_date_dt = datetime.now() - timedelta(days=self.backfill_date_interval)

        resp = requests.get(
            f"{self.api_url}/{self.user_id}/threads",
            params={
                "fields": "id,permalink,username,timestamp,text",
                "since": str(start_date_dt.isoformat()),
                "access_token": self.access_token,
                "limit": self.limit if self.limit else 100,
            },
        )
        print(resp.json())
        if resp.status_code != 200:
            raise Exception(resp.json())

        df = pd.DataFrame.from_dict(resp.json().get("data", []))

        return df

    def create_media_container(
        self,
        text: str = None,
        media_type: str = "TEXT",
        image_url: str = None,
        video_url: str = None,
        is_carousel_item: bool = False,
    ) -> dict:
        params = {
            "text": text,
            "access_token": self.access_token,
            "media_type": media_type,  # TEXT, IMAGE, VIDEO
        }

        if media_type == "IMAGE" and image_url is not None:
            params["image_url"] = image_url
        elif media_type == "VIDEO" and video_url is not None:
            params["video_url"] = video_url
        elif is_carousel_item:
            params["is_carousel_item"] = is_carousel_item

        resp = requests.post(
            f"{self.api_url}/{self.user_id}/threads",
            params=params,
        )

        if resp.status_code != 200:
            raise Exception(resp.json())

        return resp.json()

    def publish_container(self, media_id: str) -> dict:
        resp = requests.post(
            f"{self.api_url}/{self.user_id}/threads_publish",
            params={
                "creation_id": media_id,
                "access_token": self.access_token,
            },
        )

        if resp.status_code != 200:
            raise Exception(resp.json())

        return resp.json()

    def create_carousel_container(self, media_list: list, text: str = None) -> dict:
        # curl -i -X POST "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads?media_type=CAROUSEL&children=<MEDIA_ID_1>,<MEDIA_ID_2>,<MEDIA_ID_3>&access_token=<ACCESS_TOKEN>"
        media_id_list = ",".join(media_list)
        resp = requests.post(
            f"{self.api_url}/{self.user_id}/threads",
            params={
                "media_type": "CAROUSEL",
                "children": media_id_list,
                "access_token": self.access_token,
                "text": text,
            },
        )

        if resp.status_code != 200:
            raise Exception(resp.json())

        return resp.json()

    def arrange_insight_table(self) -> pd.DataFrame:
        INSIGHT_METRIC_LIST = [
            "views",
            "likes",
            "replies",
            "reposts",
            "quotes",
            "followers_count",
            # "follower_demographics",
        ]

        # get threads
        print("getting threads...")
        df_threads = self.get_threads_df()

        # get insights
        print("getting insights...")
        df_threads["insights"] = df_threads["id"].apply(self.get_threads_insights_by_id)

        # create columns for insights
        for metric in INSIGHT_METRIC_LIST:
            df_threads[metric] = df_threads["insights"].apply(
                lambda dict: dict.get(metric)
            )
            continue

        # drop insights column
        df_threads.drop(columns=["insights"], inplace=True)

        return df_threads
