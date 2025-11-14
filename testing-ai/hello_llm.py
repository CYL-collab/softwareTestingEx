"""
Hello LLM - 验证 SiliconFlow API 配置

这个脚本用于验证 SiliconFlow API 的配置是否正确。
运行此脚本前，请确保已创建 .env 文件并填入 API 密钥。

使用方法:
    python hello_llm.py
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

def main():
    # 加载环境变量
    load_dotenv()
    
    # 检查环境变量
    api_key = os.getenv("SILICONFLOW_API_KEY")
    base_url = os.getenv("SILICONFLOW_BASE_URL")
    
    if not api_key or api_key == "your_api_key_here":
        print("❌ 错误: 请在 .env 文件中配置 SILICONFLOW_API_KEY")
        print("提示: 复制 .env.example 为 .env 并填入你的 API 密钥")
        return
    
    print("🔧 配置信息:")
    print(f"   API Base URL: {base_url}")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    try:
        # 初始化客户端
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print("📡 正在调用 LLM API...")
        
        # 调用模型
        response = client.chat.completions.create(
            model="Qwen/Qwen3-8B",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Hello! Please introduce yourself in one sentence."
                }
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        # 获取响应
        assistant_message = response.choices[0].message.content
        
        print("✅ API 调用成功!")
        print()
        print("🤖 模型响应:")
        print(f"   {assistant_message}")
        print()
        print("📊 使用信息:")
        print(f"   使用的 tokens: {response.usage.total_tokens}")
        print(f"   - Prompt tokens: {response.usage.prompt_tokens}")
        print(f"   - Completion tokens: {response.usage.completion_tokens}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print()

if __name__ == "__main__":
    main()
