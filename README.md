# SDBanana for Substance 3D Designer

🍌 一个用于 Substance 3D Designer 的 AI 图像生成插件，通过第三方 API 使用 Google Nano Banana AI 生图。

- 需自行购买第三方api
- 在Settings页面填入API。目前只在yunwu/gptgod跑通，google 官方的API我这边没有条件测。
  [yunwu](https://yunwu.ai/register?aff=VE3i) | [gptgod](https://gptgod.site/#/register?invite_code=5ax35dxlk4bys0j7jnzqypwkc)

## 插件下载
[https://github.com/LiuYangArt/SDBanana/blob/main/Addon/SDBanana.zip](https://github.com/LiuYangArt/SDBanana/blob/main/Addon/SDBanana.zip)

## 项目简介

SDBanana 是一个 Substance 3D Designer 插件，允许用户直接在 Designer 中使用 AI 图像生成功能。该插件支持多个 API 提供商，包括 GPTGod NanoBanana Pro 和 Yunwu Gemini。

## 功能特性

- 选中sd节点时把节点作为生图输入
- 不选中节点时则只根据prompt 文生图


## 安装说明

1. **定位插件目录**

   Windows:
   ```
   C:\Users\<username>\Documents\Adobe\Adobe Substance 3D Designer\python\plugins
   ```



2. **复制插件文件**

   将整个 `SDBanana` 文件夹复制到上述插件目录中。

3. **重启 Substance 3D Designer**

   重启软件以加载插件。

## 使用方法

1. **打开插件面板**
   - 启动 Substance 3D Designer
   - 在 `Window` 菜单中找到 `SD Banana`
   - 点击打开面板

2. **配置 API 设置**
   - 切换到 `Settings` Tab
   - 选择你的 API Provider
   - 输入 API Base URL
   - 输入 API Key
   - 输入 Model 名称
   - 点击 `Save Settings`（当前为占位功能）

3. **生成图像**
   - 切换到 `Generate` Tab
   - 在 Prompt 输入框中输入描述
   - 选择图像尺寸
   - 点击 `Generate Image`（当前为占位功能）


