
<div align="center">

![:name](https://count.getloli.com/@astrbot_plugin_file?name=astrbot_plugin_file&theme=minecraft&padding=6&offset=0&align=top&scale=1&pixelated=1&darkmode=auto)

# FileTool - 自动文件转发插件

## 功能描述

这是一个AstrBot插件，用于自动监听群文件上传事件并转发到指定群聊。

> 基于 [astrbot_plugin_file](https://github.com/Chris95743/astrbot_plugin_file) 重构，专注于自动文件转发功能。

## 主要功能

- 自动监听所有群聊中的文件上传事件
- 支持多种文件类型：图片、视频、音频、普通文件
- 自动转发文件到指定群聊（1035079001）
- 在源群发送确认消息
- 记录详细的文件上传信息（群号、触发人、文件名、文件类型）

## 消息格式

### 转发到目标群的消息格式：
```
群号：xxxxxxx（上传文件的群聊）
触发人：xxxxxxx（QQ号）
文件名：
文件名1 [图片]
文件名2 [视频]
文件名3 [音频]
文件名4 [文件]
...
```

### 源群确认消息格式：
```
文件已转发到指定群聊
群号：xxxxxxx
触发人：xxxxxxx
文件名：
文件名1 [图片]
文件名2 [视频]
文件名3 [音频]
文件名4 [文件]
...
```

## 安装方法

1. 将插件文件夹放入AstrBot的 `data/plugins/` 目录
2. 在AstrBot WebUI的插件管理处启用插件
3. 点击"重载插件"使插件生效

## 配置说明

插件默认将文件上传信息转发到群号 `1035079001`。

如需修改目标群号，请编辑 `main.py` 文件中的 `self.target_group_id` 变量。

## 技术特点

- **多种文件检测方式**：支持文件ID、URL、直接文件对象
- **备用下载机制**：当AstrBot API不支持时，自动使用HTTP下载
- **兼容多平台**：支持不同协议端的文件格式
- **错误处理**：完善的异常处理和日志记录

## 注意事项

- 插件只处理群聊中的文件上传事件
- 私聊中的文件上传不会被处理
- 确保机器人有权限在目标群发送消息
- 确保机器人有权限读取源群的文件上传事件

## 版本信息

- 版本：1.0.0
- 作者：Mcpol
- 支持平台：所有AstrBot支持的平台
