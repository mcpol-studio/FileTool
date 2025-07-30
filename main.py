from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import File, Image, Video, Audio

@register("file_forward", "Mcpol", "群文件上传转发插件", "1.0.0", "https://github.com/mcpol-studio/file_forward_plugin")
class FileForwardPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.target_group_id = "1035079001"
        logger.info("文件转发插件已加载")

    @filter.message()
    async def handle_file_upload(self, event: AstrMessageEvent):
        """处理群文件上传事件"""
        try:
            # 添加调试日志
            logger.info(f"收到消息事件: 群号={event.group_id}, 发送者={event.get_sender_id()}, 消息内容={event.message_str[:50]}...")
            
            # 检查消息是否包含文件
            message_obj = event.message_obj
            if not message_obj:
                logger.info("消息对象为空，跳过处理")
                return
            
            # 检查消息组件中是否有文件
            file_components = []
            logger.info(f"消息组件数量: {len(message_obj.message)}")
            for i, component in enumerate(message_obj.message):
                logger.info(f"组件 {i}: {type(component)} - {component}")
                # 检查多种文件类型
                if (isinstance(component, File) or 
                    (hasattr(component, 'type') and component.type == 'file') or
                    isinstance(component, Image) or
                    isinstance(component, Video) or
                    isinstance(component, Audio)):
                    file_components.append(component)
                    logger.info(f"发现文件组件: {component}")
            
            if not file_components:
                logger.info("未发现文件组件，跳过处理")
                return
            
            # 获取群号
            group_id = event.group_id
            if not group_id:
                return
            
            # 获取发送者信息
            sender_qq = event.get_sender_id()
            
            # 构建转发消息
            forward_message = f"群号：{group_id}\n触发人：{sender_qq}\n文件名："
            
            # 添加所有文件名
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
            
            forward_message += "\n".join(file_names)
            
            # 转发到目标群
            yield event.plain_result(forward_message, target_group_id=self.target_group_id)
            logger.info(f"文件上传事件已转发到群 {self.target_group_id}")
            
            # 在源群发送确认消息
            confirm_msg = f"文件已转发到指定群聊\n群号：{group_id}\n触发人：{sender_qq}\n文件名：\n" + "\n".join(file_names)
            yield event.plain_result(confirm_msg)
                
        except Exception as e:
            logger.error(f"处理文件上传事件时出错: {e}")

    async def terminate(self):
        """插件卸载时的清理工作"""
        logger.info("文件转发插件已卸载") 