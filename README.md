# SDBanana for Substance 3D Designer
<img width="512" height="512" alt="sdbanana" src="https://github.com/user-attachments/assets/452fdd1c-6f90-4391-a1d4-4f4fa48237b0" />

🍌 一个用于 Substance 3D Designer 的 AI 图像生成插件，通过第三方 API 使用 Google Nano Banana AI 生图。

- 需自行购买第三方api
- 在Settings页面填入API。目前只在yunwu/gptgod测试过，google 官方的API我这边没有条件测。
  [yunwu](https://yunwu.ai/register?aff=VE3i) | [gptgod](https://gptgod.site/#/register?invite_code=5ax35dxlk4bys0j7jnzqypwkc)

## 插件下载
[https://github.com/LiuYangArt/SDBanana/blob/main/Addon/SDBanana.zip](https://github.com/LiuYangArt/SDBanana/blob/main/Addon/SDBanana.zip)


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
   <img width="1267" height="324" alt="image" src="https://github.com/user-attachments/assets/06e0a0f6-0326-42c7-9229-784f07886272" />



## 使用方法

1. **打开插件面板**
   - 启动 Substance 3D Designer
   - 在 `Window` 菜单中找到 `SD Banana`
   - 点击打开面板

2. **配置 API 设置**
   - 切换到 `Settings` Tab
   - 选择你的 API Provider,目前支持google官方api，openrouter，yunwu，gptgod
   - 输入 API Key
   - Save 保存设置
     <img width="663" height="335" alt="image" src="https://github.com/user-attachments/assets/72d461a9-7739-42df-98b9-1d00971268e4" />
   - 使用yunwu api时需要启用gemini相关的分组以使用gemini生图api<img width="1935" height="151" alt="image" src="https://github.com/user-attachments/assets/c43e9d7e-ccfb-4981-bcc3-4a4db7393806" />

3. **生成图像**
   - 切换到 `Generate` Tab
   - 在 Prompt 输入框中输入描述
   - 选择图像尺寸
   - 点击 `Generate Image`
   - 选中sd节点时把节点作为生图输入
   - 不选中节点时则只根据prompt 文生图
  
<img width="1845" height="1662" alt="image" src="https://github.com/user-attachments/assets/84bd147e-fd86-4f8c-932d-5cdf0202e056" />
<img width="2001" height="895" alt="image" src="https://github.com/user-attachments/assets/b9e519b9-bf82-4746-8296-f975f76a6f84" />


## 免责声明
本插件功能依赖第三方 API 服务。在使用过程中，您的数据（包括但不限于图片、提示词）将被发送至第三方服务器进行处理。开发者不对第三方服务的数据安全性、隐私保护或服务稳定性承担任何责任。请勿上传包含敏感个人信息的内容，使用本插件产生的任何数据泄露风险由用户自行承担。



---

# SDBanana for Substance 3D Designer

🍌 An AI image generation plugin for Substance 3D Designer, leveraging third-party APIs to generate images using Google Nano Banana AI.

- You need to purchase a third-party API key yourself.
- Enter the API key on the Settings page. Currently, it has only been tested with yunwu/gptgod. I don't have the conditions to test Google's official API.
  [yunwu](https://yunwu.ai/register?aff=VE3i) | [gptgod](https://gptgod.site/#/register?invite_code=5ax35dxlk4bys0j7jnzqypwkc)

## Plugin Download
[https://github.com/LiuYangArt/SDBanana/blob/main/Addon/SDBanana.zip](https://github.com/LiuYangArt/SDBanana/blob/main/Addon/SDBanana.zip)

## Features

- When an SD node is selected, the node serves as the input for image generation.
- When no node is selected, it generates images based solely on the prompt (text-to-image).

## Installation Guide

1. **Locate the Plugin Directory**

   Windows:
   ```
   C:\Users\<username>\Documents\Adobe\Adobe Substance 3D Designer\python\plugins
   ```

2. **Copy Plugin Files**

   Copy the entire `SDBanana` folder into the plugin directory mentioned above.
   <img width="1267" height="324" alt="image" src="https://github.com/user-attachments/assets/06e0a0f6-0326-42c7-9229-784f07886272" />

## How to Use

1. **Open the Plugin Panel**
   - Launch Substance 3D Designer
   - Find `SD Banana` in the `Window` menu
   - Click to open the panel

2. **Configure API Settings**
   - Switch to the `Settings` Tab
   - Select your API Provider (currently supports Google official API, Openrouter, Yunwu, Gptgod)
   - Enter your API Key
   - Click `Save` to save settings
     <img width="663" height="335" alt="image" src="https://github.com/user-attachments/assets/72d461a9-7739-42df-98b9-1d00971268e4" />
   - When using the Yunwu API, you need to enable Gemini-related groups to use the Gemini image generation API.
     <img width="1935" height="151" alt="image" src="https://github.com/user-attachments/assets/c43e9d7e-ccfb-4981-bcc3-4a4db7393806" />

3. **Generate Images**
   - Switch to the `Generate` Tab
   - Enter your description in the Prompt input box
   - Select the image size
   - Click `Generate Image`
   - When an SD node is selected, the node serves as the input for image generation.
   - When no node is selected, it generates images based solely on the prompt (text-to-image).

<img width="1845" height="1662" alt="image" src="https://github.com/user-attachments/assets/84bd147e-fd86-4f8c-932d-5cdf0202e056" />
<img width="2001" height="895" alt="image" src="https://github.com/user-attachments/assets/b9e519b9-bf82-4746-8296-f975f76a6f84" />


## Disclaimer
This plugin relies on third-party API services. Please be aware that your data (including but not limited to images and prompts) will be transmitted to external servers for processing. The developer assumes no liability for data security, privacy leaks, or service stability regarding these third-party providers. Please do not upload sensitive personal information; users assume all risks associated with data privacy when using this plugin.
