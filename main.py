from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import os
import asyncio
import aiohttp
import uuid

@register("FileTool", "Mcpol", "自动文件转发插件", "1.0.0", "https://github.com/mcpol-studio/FileTool")
class FileTool(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.target_group_id = "1035079001"  # 目标转发群号
        logger.info("FileTool 自动文件转发插件已加载")

    async def download_file(self, url: str, filename: str) -> str:
        """下载文件到本地"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # 创建临时目录
                        temp_dir = "/tmp/filetool"
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        file_path = os.path.join(temp_dir, filename)
                        with open(file_path, 'wb') as f:
                            f.write(await response.read())
                        return file_path
                    else:
                        logger.error(f"下载文件失败: HTTP {response.status}")
                        return None
        except Exception as e:
            logger.error(f"下载文件异常: {e}")
            return None

    @filter.message()
    async def handle_file_upload(self, event: AstrMessageEvent):
        """处理群文件上传事件"""
        try:
            # 检查是否为群聊消息
            if not event.group_id:
                return
            
            # 检查消息是否包含文件
            message_obj = event.message_obj
            if not message_obj:
                return
            
            # 检查消息组件中是否有文件
            file_components = []
            for component in message_obj.message:
                # 检查多种文件类型
                if (isinstance(component, File) or 
                    (hasattr(component, 'type') and component.type == 'file') or
                    isinstance(component, Image) or
                    isinstance(component, Video) or
                    isinstance(component, Audio)):
                    file_components.append(component)
            
            if not file_components:
                return
            
            # 获取发送者信息
            sender_qq = event.get_sender_id()
            group_id = event.group_id
            
            # 构建转发消息
            forward_message = f"群号：{group_id}\n触发人：{sender_qq}\n文件名："
            
            # 处理每个文件
            file_names = []
            for file_comp in file_components:
                file_name = "未知文件"
                
                # 尝试获取文件名
                if hasattr(file_comp, 'name') and file_comp.name:
                    file_name = file_comp.name
                elif hasattr(file_comp, 'file_id') and file_comp.file_id:
                    file_name = f"文件ID: {file_comp.file_id}"
                elif hasattr(file_comp, 'url') and file_comp.url:
                    file_name = f"网络文件: {file_comp.url.split('/')[-1] if '/' in file_comp.url else file_comp.url}"
                
                # 添加文件类型标识
                if isinstance(file_comp, Image):
                    file_name += " [图片]"
                elif isinstance(file_comp, Video):
                    file_name += " [视频]"
                elif isinstance(file_comp, Audio):
                    file_name += " [音频]"
                elif isinstance(file_comp, File):
                    file_name += " [文件]"
                
                file_names.append(file_name)
                
                # 尝试下载并转发文件
                try:
                    # 方式1: 使用文件ID下载
                    if hasattr(file_comp, 'file_id') and file_comp.file_id:
                        # 这里可以调用AstrBot的文件下载API
                        logger.info(f"尝试下载文件ID: {file_comp.file_id}")
                    
                    # 方式2: 使用URL下载
                    elif hasattr(file_comp, 'url') and file_comp.url:
                        downloaded_path = await self.download_file(file_comp.url, file_name)
                        if downloaded_path:
                            # 发送文件到目标群
                            yield event.chain_result([File(name=file_name, file=downloaded_path)], target_group_id=self.target_group_id)
                            logger.info(f"文件已转发到群 {self.target_group_id}")
                    
                    # 方式3: 直接使用文件对象
                    elif hasattr(file_comp, 'file') and file_comp.file:
                        yield event.chain_result([file_comp], target_group_id=self.target_group_id)
                        logger.info(f"文件已转发到群 {self.target_group_id}")
                        
                except Exception as e:
                    logger.error(f"转发文件失败: {e}")
            
            # 发送通知消息到目标群
            forward_message += "\n".join(file_names)
            yield event.plain_result(forward_message, target_group_id=self.target_group_id)
            
            # 在源群发送确认消息
            confirm_msg = f"文件已转发到指定群聊\n群号：{group_id}\n触发人：{sender_qq}\n文件名：\n" + "\n".join(file_names)
            yield event.plain_result(confirm_msg)
            
            logger.info(f"文件上传事件处理完成，共处理 {len(file_components)} 个文件")
                
        except Exception as e:
            logger.error(f"处理文件上传事件时出错: {e}")

    async def terminate(self):
        """插件卸载时的清理工作"""
        logger.info("FileTool 插件已卸载")
