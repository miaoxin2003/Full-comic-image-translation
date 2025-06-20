# API问题解决指南 🔧

## 🚨 "choices" 错误解决方案

### 问题描述
出现 `全图翻译调用失败: 'choices'` 错误，表明API返回的响应中缺少 `choices` 字段。

### 🔍 可能原因

1. **模型不支持视觉功能** ⭐ 最常见原因
2. **API配置错误**
3. **API密钥无效或权限不足**
4. **网络连接问题**
5. **API服务商响应格式异常**

## 🛠️ 解决步骤

### 步骤1: 运行诊断工具

```bash
cd ai输出/ai1
python api_diagnostic.py
```

这个工具会自动检查：
- ✅ API配置是否正确
- ✅ 网络连接是否正常
- ✅ 模型是否支持视觉功能

### 步骤2: 检查模型配置

#### 支持视觉的模型列表：

**🆓 免费模型 (OpenRouter)**
- `opengvlab/internvl3-14b:free` ⭐ 推荐
- `qwen/qwen-2-vl-7b-instruct:free`

**💰 付费模型**
- OpenAI: `gpt-4o`, `gpt-4o-mini`
- Anthropic: `claude-3-5-sonnet-20241022`
- Google: `gemini-1.5-pro`, `gemini-1.5-flash`

#### 不支持视觉的模型（会导致错误）：
- ❌ `gpt-3.5-turbo`
- ❌ `claude-3-haiku` (文本版)
- ❌ 大部分纯文本模型

### 步骤3: 快速修复配置

```bash
python fix_api_config.py
```

选择推荐的配置方案：

#### 🆓 方案1: OpenRouter + InternVL (免费)
```
服务商: OpenRouter
模型: opengvlab/internvl3-14b:free
基础URL: https://openrouter.ai/api/v1
```

#### 💰 方案2: OpenAI + GPT-4o-mini
```
服务商: OpenAI  
模型: gpt-4o-mini
基础URL: https://api.openai.com/v1
```

#### 💰 方案3: Anthropic + Claude
```
服务商: Anthropic
模型: claude-3-5-sonnet-20241022
基础URL: https://api.anthropic.com/v1
```

## 🎯 推荐解决方案

### 对于新用户（推荐）

1. **注册OpenRouter账号**
   - 访问: https://openrouter.ai/
   - 注册并获取API密钥

2. **配置OpenRouter**
   ```bash
   python fix_api_config.py
   ```
   选择选项1，输入API密钥

3. **测试配置**
   ```bash
   python api_diagnostic.py
   ```

### 对于现有用户

1. **检查当前模型**
   - 打开应用，点击"设置"
   - 查看"模型设置"标签页
   - 确认模型支持视觉功能

2. **更换支持视觉的模型**
   - 在模型列表中选择支持视觉的模型
   - 或在"自定义模型"中输入: `opengvlab/internvl3-14b:free`

## 🔧 手动配置步骤

### OpenRouter配置
1. 打开应用设置
2. 选择"OpenRouter"
3. 填写配置：
   - API密钥: 你的OpenRouter密钥
   - 基础URL: `https://openrouter.ai/api/v1`
   - HTTP Referer: `https://github.com/your-username/comic-translator`
   - X-Title: `Comic Translator`
4. 模型设置：
   - 选择或输入: `opengvlab/internvl3-14b:free`

### OpenAI配置
1. 选择"OpenAI"
2. 填写配置：
   - API密钥: 你的OpenAI密钥
   - 基础URL: `https://api.openai.com/v1`
3. 模型设置：
   - 选择: `gpt-4o-mini`

## 🚨 常见错误及解决

### 错误1: "API密钥未配置"
**解决**: 在设置中正确填写API密钥

### 错误2: "HTTP错误: 401"
**解决**: API密钥无效，请检查密钥是否正确

### 错误3: "HTTP错误: 403"
**解决**: API密钥权限不足或余额不足

### 错误4: "模型不支持视觉功能"
**解决**: 更换为支持视觉的模型

### 错误5: "网络连接失败"
**解决**: 检查网络连接，可能需要代理

## 📋 验证清单

配置完成后，请确认：

- [ ] API服务商选择正确
- [ ] API密钥已正确填写
- [ ] 基础URL格式正确
- [ ] 模型支持视觉功能
- [ ] 网络连接正常
- [ ] 运行诊断工具通过所有检查

## 🆘 仍然有问题？

如果按照上述步骤仍然无法解决，请：

1. **运行完整诊断**
   ```bash
   python api_diagnostic.py
   ```

2. **查看详细错误信息**
   - 改进后的代码会显示详细的调试信息
   - 包括HTTP状态码、响应结构等

3. **尝试不同的模型**
   - 从推荐列表中选择其他模型
   - 确认模型名称拼写正确

4. **检查网络环境**
   - 确认可以访问API服务商网站
   - 如在中国大陆，可能需要代理访问OpenAI

## 💡 最佳实践

1. **优先使用OpenRouter**
   - 提供多种免费模型
   - 无需代理即可访问
   - 支持多种视觉模型

2. **定期检查配置**
   - 使用诊断工具定期检查
   - 确保API密钥有效

3. **备用方案**
   - 配置多个API服务商
   - 在一个失效时快速切换

现在您应该能够成功使用漫画翻译功能了！🎉
