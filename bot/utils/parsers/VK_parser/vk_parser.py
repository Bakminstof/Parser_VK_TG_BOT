import os.path
import random
import threading
import time
import youtube_dl
import requests
import logging.config

from typing import List, Tuple
from pathlib import Path

from data import ACCESS_TOKEN, VERSION_VK_API
from utils.logging import dict_config, async_dec_logger, sync_dec_logger
from utils.parsers.meta_display_cls import MetaDisplayCLS
from utils.parsers.VK_parser.vk_post_cls import Attachment, VKPost

logging.config.dictConfig(dict_config)
vk_parser_logger = logging.getLogger('vk_parser')


@async_dec_logger(vk_parser_logger)
async def get_group(group: int | str) -> str | Tuple[int, str]:
    main_url = 'https://api.vk.com/method/{method}'
    method = 'groups.getById'

    url = main_url.format(method=method)

    params = {
        'v': VERSION_VK_API,
        'access_token': ACCESS_TOKEN,
        'group_ids': [group],
        'fields': 'can_post, can_see_all_posts'
    }
    try:
        response = requests.get(url, params=params, timeout=30)  # todo request exc
        groups = response.json()

        er = groups.get('error')

        if er:
            return 'Bad'
        else:
            is_closed = groups.get('response')[0].get('is_closed')

            if is_closed:
                return 'Closed'
            else:
                can_see_all_posts = groups.get('response')[0].get('can_see_all_posts')

                if can_see_all_posts:
                    id_ = groups.get('response')[0].get('id')
                    name = groups.get('response')[0].get('name', groups.get('response')[0].get('screen_name'))

                    return id_, name

                else:
                    return 'Cant see all posts'
    except Exception as ex:
        vk_parser_logger.exception('Exception: {}'.format(ex))


class VKParser(MetaDisplayCLS):
    __ID = 0

    def __init__(
            self,
            group_id: int,
            group_url: str,
            max_posts: int = 40,
            timeout: int = 150,
            post_ids: List[int] | None = None
    ):
        if post_ids is None:
            post_ids: List[int] = []

        VKParser.__ID += 1

        self.id = VKParser.__ID
        self.name = 'VK parser'

        self.__vk_token = ACCESS_TOKEN
        self.version_vk_api = VERSION_VK_API
        self.main_url = 'https://api.vk.com/method/{method}'
        self.timeout = timeout

        self.max_posts = max_posts

        self.group_name = group_url.split('/')[-1]
        self.group_id = group_id

        self.__logging_main_str = '({name} <{id}>)({group}): '.format(
            name=self.name,
            id=self.id,
            group=self.group_name
        ) + '{}'

        self.__content_dir = Path(__file__).parent / 'content'
        self.__content_dir = self.__content_dir.absolute()

        self.group_content_dir = self.__content_dir / self.group_name
        self.group_content_dir = self.group_content_dir.absolute()

        self.posts: List[VKPost] = []
        self.post_ids = post_ids

        self.__check_exist_dir()

    # Отправка постов
    # def send_post(self, group_name: str | int):
    #     id_, _ = get_group(group_name)
    #
    #     method = 'wall.post'
    #
    #     url = self.main_url.format(method=method)
    #
    #     for post in self.posts:
    #         params = {
    #             'v': self.version_vk_api,
    #             'access_token': ACCESS_TOKEN,
    #             'owner_id': -id_
    #         }
    #
    #         params.update(post.as_dict())
    #
    #         response = requests.get(url, params=params)  # todo request exc
    #         res = response.json()
    #
    #         time.sleep(0.4)
    #         # with open('res.json', 'w') as file:
    #         #     file.write(json.dumps(res, indent=4, ensure_ascii=False))

    @sync_dec_logger(vk_parser_logger)
    def __get_video_url(self, url: str, params: dict, post_id: int) -> str:
        for _ in range(2):
            try:
                resp = requests.get(url=url, params=params, timeout=self.timeout)
                res = resp.json()
                url = res['response']['items'][0]['player']

                log_ = 'Post: ({}) Get video url'.format(post_id)
                vk_parser_logger.debug(self.__logging_main_str.format(log_))

                return url
            except Exception as ex:
                log_ = 'Post: ({}) Exception\n: {}'.format(post_id, ex)
                vk_parser_logger.exception(self.__logging_main_str.format(log_))
                time.sleep(random.uniform(1, 4))
        else:
            log_ = 'Post: ({}) Can\'t get video'.format(post_id)
            vk_parser_logger.exception(self.__logging_main_str.format(log_))

    @sync_dec_logger(vk_parser_logger)
    def __check_exist_dir(self) -> None:
        log_ = 'Check group dir'
        vk_parser_logger.debug(self.__logging_main_str.format(log_))

        if not os.path.exists(self.group_content_dir):
            os.mkdir(self.group_content_dir)

            log_ = 'Create group dir'
            vk_parser_logger.debug(self.__logging_main_str.format(log_))

    @sync_dec_logger(vk_parser_logger)
    def __download_photo(self, url: str, file_path: str, post_id: int, params: dict = None) -> None:
        log_ = 'Post: ({}) Start download photo: `{}`'.format(post_id, file_path)
        vk_parser_logger.info(self.__logging_main_str.format(log_))

        for _ in range(2):
            try:
                resp = requests.get(url=url, params=params, timeout=self.timeout)

                if not os.path.exists(file_path):
                    with open(file_path, 'wb') as file:
                        file.write(resp.content)

                    log_ = 'Post: ({}) Photo download complete: `{}`'.format(post_id, file_path)
                    vk_parser_logger.info(self.__logging_main_str.format(log_))

                    break

                else:
                    log_ = 'Post: ({}) Photo already exists: `{}`'.format(post_id, file_path)
                    vk_parser_logger.warning(self.__logging_main_str.format(log_))

            except Exception as ex:
                log_ = 'Post: ({}) Exception, `{path}`\n: {ex}'.format(post_id, path=file_path, ex=ex)
                vk_parser_logger.exception(self.__logging_main_str.format(log_))
                time.sleep(random.uniform(1, 4))

    @sync_dec_logger(vk_parser_logger)
    def __download_video(self, url: str, file_path: str, post_id: int) -> bool:
        log_ = 'Post: ({}) Start download video: `{}`'.format(post_id, file_path)
        vk_parser_logger.info(self.__logging_main_str.format(log_))

        ydl_otp = {
            'outtmpl': str(file_path),
        }

        if not os.path.exists(file_path):
            try:
                with youtube_dl.YoutubeDL(ydl_otp) as ydl:
                    video_info = ydl.extract_info(url)

                    video_duration = video_info['duration']

                    if video_duration <= 600:
                        ydl.download([url])

                        log_ = 'Post: ({}) Video download complete: `{}`'.format(post_id, file_path)
                        vk_parser_logger.info(self.__logging_main_str.format(log_))

                        return True

                    else:
                        log_ = 'Post: ({})  Video longer than 10 minutes: `{}`'.format(post_id, file_path)
                        vk_parser_logger.warning(self.__logging_main_str.format(log_))

                        return False

            except Exception as ex:
                log_ = 'Post: ({}) Exception, `{path}`\n: {ex}'.format(post_id, path=file_path, ex=ex)
                vk_parser_logger.exception(self.__logging_main_str.format(log_))
                return False
        else:
            log_ = 'Post: ({}) Video already exists: `{}`'.format(post_id, file_path)
            vk_parser_logger.warning(self.__logging_main_str.format(log_))

            return False

    @sync_dec_logger(vk_parser_logger)
    def start(self):
        log_ = 'Start VK parser'
        vk_parser_logger.debug(self.__logging_main_str.format(log_))

        self.pars_wall(self.max_posts)

    @sync_dec_logger(vk_parser_logger)
    def pars_wall(self, post_count: int):
        f"""
        Собирает последние {post_count} постов
        """
        posts = []
        post_ids = []

        method = 'wall.get'
        params = {
            'v': self.version_vk_api,
            'access_token': self.__vk_token,
            'count': post_count,
            'owner_id': -self.group_id
        }

        url = self.main_url.format(method=method)

        for _ in range(2):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                posts_json = response.json()

                log_ = 'Get wall JSON: {}'.format(posts_json)
                vk_parser_logger.info(self.__logging_main_str.format(log_))
                break

            except Exception as ex:
                log_ = 'Exception: {}'.format(ex)
                vk_parser_logger.exception(self.__logging_main_str.format(log_))
                time.sleep(random.uniform(1, 4))

                continue

        else:
            log_ = 'Request error'
            vk_parser_logger.warning(self.__logging_main_str.format(log_))

            return None

        workers = []

        for p in posts_json['response']['items']:
            attachments = p.get('attachments', False)
            post_id = p.get('id')

            if post_id in self.post_ids:
                continue

            post_dir_local_path = self.group_content_dir / str(post_id)
            post_dir_local_path = post_dir_local_path.absolute()

            if not os.path.exists(post_dir_local_path):
                log_ = 'Post: ({}) Create post dir: {}'.format(post_id, post_dir_local_path)
                vk_parser_logger.debug(self.__logging_main_str.format(log_))

                os.mkdir(post_dir_local_path)

            post_ids.append(post_id)

            post = VKPost(
                id_=post_id,
                owner_id=None,
                message=p.get('text'),
                attachments=[],
                local_path=post_dir_local_path
            )

            if attachments:
                log_ = 'Post: ({}) Start get attachments ({})'.format(post_id, len(attachments))
                vk_parser_logger.debug(self.__logging_main_str.format(log_))

                for item in attachments:
                    item_type = item.get('type')

                    if item_type == 'photo':
                        photo_url = item.get('photo', {}).get('sizes', {})[-1].get('url')
                        content_id = item.get(item_type).get('id')
                        owner_id = item.get('photo', {}).get('owner_id')
                        content_type = 'jpg'

                        file_path = post_dir_local_path / '{}.{}'.format(content_id, content_type)
                        file_path = file_path.absolute()

                        thread = threading.Thread(
                            target=self.__download_photo,
                            args=(photo_url, file_path, post_id)
                        )
                        thread.start()
                        workers.append(thread)

                        log_ = 'Post: ({}) Detected photo: {}'.format(post_id, file_path)
                        vk_parser_logger.debug(self.__logging_main_str.format(log_))

                    elif item_type == 'video':
                        method = 'video.get'

                        video_access_key = item.get('video', {}).get('access_key')
                        video_id = item.get('video', {}).get('id')
                        video_owner_id = item.get('video', {}).get('owner_id')
                        owner_id = video_owner_id
                        content_id = item.get(item_type).get('id')
                        content_type = 'mp4'

                        video_params = {
                            'v': self.version_vk_api,
                            'access_token': self.__vk_token,
                            'videos': '{video_owner_id}_{video_id}_{video_access_key}'.format(
                                video_owner_id=video_owner_id,
                                video_id=video_id,
                                video_access_key=video_access_key
                            )
                        }

                        video_url = self.main_url.format(method=method)
                        video_url = self.__get_video_url(video_url, video_params, post_id)

                        file_path = post_dir_local_path / '{}.{}'.format(content_id, content_type)
                        file_path = file_path.absolute()

                        thread = threading.Thread(
                            target=self.__download_video,
                            args=(video_url, file_path, post_id)
                        )
                        thread.start()
                        workers.append(thread)

                        log_ = 'Post: ({}) Detected video: {}'.format(post_id, file_path)
                        vk_parser_logger.debug(self.__logging_main_str.format(log_))

                    else:
                        log_ = 'Post: ({}) Unsupported item type: {}'.format(post_id, item_type)
                        vk_parser_logger.info(self.__logging_main_str.format(log_))

                        continue

                    attachment = Attachment(
                        type_=item_type,
                        owner_id=owner_id,
                        media_id=content_id,
                        local_path=file_path,
                    )

                    post.attachments.append(attachment)

                    time.sleep(0.3)

            posts.append(post)

        for worker in workers:
            worker.join(self.timeout)

        self.posts = posts
        self.post_ids = post_ids

        log_ = 'Completed {} VK posts: {}'.format(len(self.posts), self.posts)
        vk_parser_logger.debug(self.__logging_main_str.format(log_))
