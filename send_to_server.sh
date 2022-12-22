#!/usr/bin/env bash
sudo rsync -Praz \
-e 'ssh -p 2323' \
--exclude=.git \
--exclude=.idea \
--exclude=__pycache__ \
--exclude=.gitignore \
--exclude=send_to_server.sh \
--exclude=ENV_Parser \
/home/andrey/my_proj/Parser_VK_TG_BOT/ \
bakminstof@192.168.1.38:/home/bakminstof/projects/parser_vk_tg_bot/bot/
