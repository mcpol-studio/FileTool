from astrbot.api.message_components import *
from astrbot.api.event import AstrMessageEvent, MessageEventResult
from astrbot.core.star.register.star_handler import register_event_message_type
from astrbot.core.star.filter.event_message_type import EventMessageType
from astrbot.api import AstrBotConfig, logger
from astrbot.api.star import Context, Star, register
from astrbot.core.message.components import File, Plain
from astrbot.core.platform.message_type import MessageType
import os
import shutil
import time
import asyncio
import aiohttp
import uuid

# 创建配置对象
# 注册插件的装饰器
@register("文件操作", "Chris", "一个简单的文件发送、删除、移动、复制和查看文件夹内容插件", "1.2.0")
class FileSenderPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.base_path = config.get('FileBasePath', '/default/path')  # 配置文件中的基础路径
        self.user_waiting = {}  # 等待上传文件的用户



    # 根据路径发送文件
    async def send_file(self, event: AstrMessageEvent, file_path: str):
        full_file_path = os.path.join(self.base_path, file_path)

        # 检查文件是否存在
        if not os.path.exists(full_file_path):
            yield event.plain_result(f"文件 {file_path} 不存在，请检查路径。")
            return

        # 检查文件是否为文件而非文件夹
        if os.path.isdir(full_file_path):
            yield event.plain_result(f"指定的路径是一个目录，而不是文件：{file_path}")
            return

        # 检查文件大小（限制为2GB）
        file_size = os.path.getsize(full_file_path)
        if file_size == 0:
            yield event.plain_result(f"文件 {file_path} 是空文件，无法发送。")
            return
        if file_size > 2 * 1024 * 1024 * 1024:  # 2GB
            yield event.plain_result(f"文件 {file_path} 大小超过2GB限制，无法发送。")
            return

        # 获取文件名（不带路径）
        file_name = os.path.basename(file_path)

        # 检查文件是否可读
        try:
            with open(full_file_path, 'rb') as f:
                f.read(1)  # 测试读取
        except Exception as e:
            yield event.plain_result(f"无法读取文件 {file_path}: {str(e)}")
            return

        # 发送文件
        yield event.plain_result(f"开始发送文件 {file_name}...")
        yield event.plain_result(f"文件路径: {full_file_path}")
        yield event.plain_result(f"文件大小: {file_size / 1024:.2f} KB")
        
        try:
            yield event.chain_result([File(name=file_name, file=full_file_path)])
            yield event.plain_result(f"文件 {file_name} 已发送。")
        except Exception as e:
            yield event.plain_result(f"发送文件失败: {str(e)}")
            yield event.plain_result("可能的原因:")
            yield event.plain_result("1. 文件路径包含特殊字符")
            yield event.plain_result("2. 文件大小超过平台限制")
            yield event.plain_result("3. 文件类型不被支持")
            yield event.plain_result("4. 机器人没有文件访问权限")

    # 根据路径删除文件
    async def delete_file(self, event: AstrMessageEvent, file_path: str):
        full_file_path = os.path.join(self.base_path, file_path)

        # 检查文件是否存在
        if not os.path.exists(full_file_path):
            yield event.plain_result(f"文件 {file_path} 不存在，请检查路径。")
            return

        # 检查文件是否为文件而非文件夹
        if os.path.isdir(full_file_path):
            yield event.plain_result(f"指定的路径是一个目录，而不是文件：{file_path}")
            return

        try:
            # 删除文件
            os.remove(full_file_path)
            yield event.plain_result(f"文件 {file_path} 已成功删除。")
        except Exception as e:
            yield event.plain_result(f"删除文件时发生错误: {str(e)}")

    # 根据路径删除目录
    async def delete_directory(self, event: AstrMessageEvent, dir_path: str):
        full_dir_path = os.path.join(self.base_path, dir_path)

        # 检查目录是否存在
        if not os.path.exists(full_dir_path):
            yield event.plain_result(f"目录 {dir_path} 不存在，请检查路径。")
            return

        # 检查是否是目录
        if not os.path.isdir(full_dir_path):
            yield event.plain_result(f"指定路径 {dir_path} 不是一个目录。")
            return

        try:
            # 删除目录及其中所有内容
            shutil.rmtree(full_dir_path)
            yield event.plain_result(f"目录 {dir_path} 已成功删除。")
        except Exception as e:
            yield event.plain_result(f"删除目录时发生错误: {str(e)}")

    # 查看目录内容
    async def list_files(self, event: AstrMessageEvent, dir_path: str):
        full_dir_path = os.path.join(self.base_path, dir_path)

        # 检查目录是否存在
        if not os.path.exists(full_dir_path):
            yield event.plain_result(f"目录 {dir_path} 不存在，请检查路径。")
            return

        # 检查是否是目录
        if not os.path.isdir(full_dir_path):
            yield event.plain_result(f"指定路径 {dir_path} 不是一个目录。")
            return

        # 获取目录内容
        try:
            files = os.listdir(full_dir_path)
            if not files:
                yield event.plain_result(f"目录 {dir_path} 是空的。")
                return

            # 格式化文件和文件夹输出
            result = ""
            for file in files:
                full_path = os.path.join(full_dir_path, file)
                if os.path.isdir(full_path):
                    result += f"/{file}\n"  # 文件夹前加 '/'
                else:
                    result += f"{file}\n"  # 文件不加 '/'

            yield event.plain_result(f"目录 {dir_path} 的内容：\n{result}")
        except Exception as e:
            yield event.plain_result(f"读取目录时发生错误: {str(e)}")

    # 移动文件或目录
    async def move(self, event: AstrMessageEvent, source_path: str, destination_path: str):
        source_full_path = os.path.join(self.base_path, source_path)
        destination_full_path = os.path.join(self.base_path, destination_path)

        # 检查源文件/目录是否存在
        if not os.path.exists(source_full_path):
            yield event.plain_result(f"源路径 {source_path} 不存在，请检查路径。")
            return

        try:
            # 移动文件或目录
            shutil.move(source_full_path, destination_full_path)
            yield event.plain_result(f"文件/目录 {source_path} 已成功移动到 {destination_path}。")
        except Exception as e:
            yield event.plain_result(f"移动文件/目录时发生错误: {str(e)}")

    # 复制文件或目录
    async def copy(self, event: AstrMessageEvent, source_path: str, destination_path: str):
        source_full_path = os.path.join(self.base_path, source_path)
        destination_full_path = os.path.join(self.base_path, destination_path)

        # 检查源文件/目录是否存在
        if not os.path.exists(source_full_path):
            yield event.plain_result(f"源路径 {source_path} 不存在，请检查路径。")
            return

        try:
            # 复制文件或目录
            if os.path.isdir(source_full_path):
                shutil.copytree(source_full_path, destination_full_path)
            else:
                shutil.copy2(source_full_path, destination_full_path)
            yield event.plain_result(f"文件/目录 {source_path} 已成功复制到 {destination_path}。")
        except Exception as e:
            yield event.plain_result(f"复制文件/目录时发生错误: {str(e)}")

    # 处理文件上传到指定目录
    async def upload_file(self, event: AstrMessageEvent, file_path: str, file_content: bytes, file_name: str):
        full_file_path = os.path.join(self.base_path, file_path, file_name)

    @register_event_message_type(EventMessageType.ALL)
    async def on_message(self, *args, **kwargs):
            logger.info(f"on_message received args: {args}, kwargs: {kwargs}")
            # 检查是否是文件消息
            if len(args) > 0 and isinstance(args[0], AstrMessageEvent):
                event = args[0]
                if event.message_type == EventMessageType.FILE:
                    # 遍历消息链，查找文件组件
                    for component in event.message:
                        if isinstance(component, File):
                            file_id = component.file_id
                            file_name = component.file_name
                            # 尝试转发文件
                            try:
                                # 获取文件下载链接
                                # 假设 context 对象在 kwargs 中或者可以通过 self.context 访问
                                context = kwargs.get('context') or self.context
                                file_url = await context.get_file_url(file_id)
                                if file_url:
                                    # 转发文件，这里需要根据实际的转发API进行调整
                                    # 假设 context.send_file 可以直接转发文件URL
                                    await context.send_file(event.channel_id, file_url, file_name)
                                    logger.info(f"Successfully forwarded file: {file_name} from {event.sender.name}")
                                else:
                                    logger.warning(f"Could not get file URL for file_id: {file_id}")
                            except Exception as e:
                                logger.error(f"Error forwarding file {file_name}: {e}")
                            break # 找到文件后即可退出循环
                file_url = component.url
                file_name = component.name
                # 转发文件
                yield event.chain_result([File(name=file_name, url=file_url)])
                if file_name:
                    if file_url:
                        logger.info(f"检测到文件，URL: {file_url}, 名称: {file_name}")
                        source_path = file_url
                    elif component.path:
                        logger.info(f"检测到文件，本地路径: {component.path}, 名称: {file_name}")
                        source_path = component.path
                    else:
                        logger.warning(f"文件 {file_name} 没有可用的 URL 或本地路径。")
                        continue

                    try:
                        # 获取当前消息的群组ID作为目标群组ID
                        current_group_id = event.group_id
                        if not current_group_id:
                            logger.warning(f"无法获取当前消息的群组ID，跳过文件转发。")
                            continue

                        # 下载文件
                        download_dir = os.path.join(self.base_path, "downloads")
                        os.makedirs(download_dir, exist_ok=True)
                        local_file_path = os.path.join(download_dir, file_name)

                        if source_path.startswith("http"):
                            async with aiohttp.ClientSession() as session:
                                async with session.get(source_path) as response:
                                    response.raise_for_status()
                                    with open(local_file_path, 'wb') as f:
                                        while True:
                                            chunk = await response.content.read(8192)
                                            if not chunk:
                                                break
                                            f.write(chunk)
                            logger.info(f"文件 {file_name} 从 URL 下载完成。")
                        elif os.path.exists(source_path):
                            shutil.copy2(source_path, local_file_path)
                            logger.info(f"文件 {file_name} 从本地路径复制完成。")
                        else:
                            yield event.plain_result(f"文件 {file_name} 无法下载或复制，源路径无效。")
                            logger.error(f"文件 {file_name} 源路径无效: {source_path}")
                            continue

                        await self.context.send_message(
                            session=f"qq:{MessageType.FILE_MESSAGE.value}:{current_group_id}",
                            message_chain=[Plain(text=f"收到文件：{file_name}，已下载到本地。正在转发..."), File(name=file_name, file=local_file_path)]
                        )
                        yield event.plain_result(f"文件 {file_name} 已转发到群聊 {current_group_id}。")
                    except Exception as e:
                        yield event.plain_result(f"处理文件 {file_name} 失败: {e}")
                        logger.error(f"处理文件 {file_name} 失败: {e}")
                break
