# main.py for file_forwarder plugin

from astrbot.core.star import Star
from astrbot.core.platform import AstrMessageEvent
from astrbot.core.message import MessageChain, File, Plain
from astrbot.core.star.star_tools import StarTools

class FileForwarder(Star):
    def __init__(self, context):
        super().__init__(context)
        self.target_qq = "1035079001" # 目标QQ号

    async def on_message(self, event: AstrMessageEvent):
        # 避免循环转发，如果当前会话ID与目标QQ号相同，则不进行转发
        if event.get_session_id() == str(self.target_qq):
            return

        # 检查消息中是否包含文件组件
        for component in event.message_obj.chain:
            if isinstance(component, File):
                file_name = component.name
                file_path = await component.get_file() # 异步获取本地文件路径，确保文件被下载
                file_url = component.url # 获取文件URL

                if not file_path: # 如果文件路径为空，尝试使用URL
                    self.logger.warning(f"无法获取文件 {file_name} 的本地路径，尝试使用URL转发。")
                    # 如果file_path为空，File组件会尝试从url下载，或者直接使用url
                    forward_file_component = File(name=file_name, url=file_url)
                else:
                    forward_file_component = File(name=file_name, file_=file_path)

                # 构造转发消息
                forward_message = MessageChain([
                    Plain(f"收到文件: {file_name}\n"),
                    forward_file_component # 转发文件
                ])

                # 转发到目标QQ
                await StarTools.send_message(
                    platform="aiocqhttp", # 转发到aiocqhttp平台，icqq通常是go-cqhttp的实现
                    session=str(self.target_qq),
                    message_chain=forward_message
                )
                self.logger.info(f"文件 {file_name} 已转发到 {self.target_qq}")
                return # 处理完文件后停止进一步处理

        return # 如果没有文件，继续处理其他插件