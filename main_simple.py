from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import File

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
            # 检查消息是否包含文件
            message_obj = event.message_obj
            if not message_obj:
                return
            
            # 检查消息组件中是否有文件
            file_components = []
            for component in message_obj.message:
                if isinstance(component, File):
                    file_components.append(component)
            
            if not file_components:
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
                if hasattr(file_comp, 'name') and file_comp.name:
                    file_names.append(file_comp.name)
                elif hasattr(file_comp, 'file_id'):
                    file_names.append(f"文件ID: {file_comp.file_id}")
                else:
                    file_names.append("未知文件")
            
            forward_message += "\n".join(file_names)
            
            # 转发到目标群
            try:
                # 发送文本消息到目标群
                yield event.plain_result(forward_message, target_group_id=self.target_group_id)
                logger.info(f"文件上传事件已转发到群 {self.target_group_id}")
                
                # 在源群发送确认消息
                confirm_msg = f"文件已转发到指定群聊\n群号：{group_id}\n触发人：{sender_qq}\n文件名：\n" + "\n".join(file_names)
                yield event.plain_result(confirm_msg)
                
            except Exception as e:
                logger.error(f"转发文件消息失败: {e}")
                
        except Exception as e:
            logger.error(f"处理文件上传事件时出错: {e}")

    async def terminate(self):
        """插件卸载时的清理工作"""
        logger.info("文件转发插件已卸载") 