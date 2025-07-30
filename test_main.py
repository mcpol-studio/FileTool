from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("file_forward_test", "Mcpol", "文件转发测试插件", "1.0.0", "https://github.com/your-repo")
class FileForwardTestPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.target_group_id = "1035079001"
        logger.info("文件转发测试插件已加载")

    @filter.message()
    async def handle_all_messages(self, event: AstrMessageEvent):
        """处理所有消息事件进行测试"""
        try:
            # 记录所有消息
            logger.info(f"=== 收到消息事件 ===")
            logger.info(f"群号: {event.group_id}")
            logger.info(f"发送者: {event.get_sender_id()}")
            logger.info(f"消息内容: {event.message_str}")
            
            # 检查消息对象
            message_obj = event.message_obj
            if message_obj:
                logger.info(f"消息对象类型: {type(message_obj)}")
                logger.info(f"消息组件数量: {len(message_obj.message)}")
                
                for i, component in enumerate(message_obj.message):
                    logger.info(f"组件 {i}: {type(component)} - {component}")
                    
                    # 检查是否是文件
                    if hasattr(component, 'type'):
                        logger.info(f"组件类型: {component.type}")
                    if hasattr(component, 'name'):
                        logger.info(f"组件名称: {component.name}")
                    if hasattr(component, 'file_id'):
                        logger.info(f"文件ID: {component.file_id}")
            else:
                logger.info("消息对象为空")
            
            logger.info("=== 消息处理完成 ===")
            
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")

    async def terminate(self):
        """插件卸载时的清理工作"""
        logger.info("文件转发测试插件已卸载") 