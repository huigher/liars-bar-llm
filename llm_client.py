from openai import OpenAI
from volcenginesdkarkruntime import Ark
import os
import traceback

ALIYUN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
ALIYUN_API_KEY = os.getenv("ALIYUN_API_KEY")
HUOSHAN_API_URL = "https://ark.cn-beijing.volces.com/api/v3"
HUOSHAN_API_KEY = os.getenv("HUOSHAN_API_KEY")
QCLOUD_API_URL = "https://api.hunyuan.cloud.tencent.com/v1"
QCLOUD_API_KEY = os.getenv("QCLOUD_API_KEY")

QWEN_MODEL_NAME = "qwen-max-2025-01-25"
QWEN_THINKING_MODEL_NAME = "qwq-plus-2025-03-05"
DEEPSEEK_MODEL_NAME = "deepseek-r1"
DOUBAO_MODEL_NAME = "doubao-1.5-pro-32k-250115"
HUNYUAN_MODEL_NAME = "hunyuan-turbos-20250313"

MODEL_NICKNAME_DB = {
    QWEN_MODEL_NAME: "小紫",
    QWEN_THINKING_MODEL_NAME: "小丁",
    DEEPSEEK_MODEL_NAME: "小蓝",
    DOUBAO_MODEL_NAME: "小豆",
    HUNYUAN_MODEL_NAME: "小鹅"
}

MODEL_API_URL_DB = {
    QWEN_MODEL_NAME: ALIYUN_API_URL,
    QWEN_THINKING_MODEL_NAME: ALIYUN_API_URL,
    DEEPSEEK_MODEL_NAME: ALIYUN_API_URL,
    DOUBAO_MODEL_NAME: HUOSHAN_API_URL,
    HUNYUAN_MODEL_NAME: QCLOUD_API_URL
}
API_KEY_DB = {
    QWEN_MODEL_NAME: ALIYUN_API_KEY,
    QWEN_THINKING_MODEL_NAME: ALIYUN_API_KEY,
    DEEPSEEK_MODEL_NAME: ALIYUN_API_KEY,
    DOUBAO_MODEL_NAME: HUOSHAN_API_KEY,
    HUNYUAN_MODEL_NAME: QCLOUD_API_KEY
}


class LLMClient:
    def __init__(self, model_name):
        """初始化LLM客户端，隐去实现细节，只需要传入各平台的模型名称"""
        self.model_name = model_name
        if model_name in [QWEN_MODEL_NAME, QWEN_THINKING_MODEL_NAME, DEEPSEEK_MODEL_NAME]:
            self.client = OpenAI(
                api_key=ALIYUN_API_KEY,
                base_url=ALIYUN_API_URL
            )
            self.chat = self.openai_compatible_chat_stream
        elif model_name in [HUNYUAN_MODEL_NAME, ]:
            self.client = OpenAI(
                api_key=QCLOUD_API_KEY,
                base_url=QCLOUD_API_URL
            )
            self.chat = self.openai_compatible_chat_stream
        elif model_name in [DOUBAO_MODEL_NAME, ]:
            self.client = Ark(api_key=HUOSHAN_API_KEY)
            self.chat = self.huoshan_chat_stream
        else:
            raise ValueError("不支持的模型名称")

    def chat_old(self, messages):
        """与LLM交互
        
        Args:
            messages: 消息列表
            model: 使用的LLM模型
        
        Returns:
            tuple: (content, reasoning_content)
        """
        try:
            print(f"LLM请求: {messages}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=False
            )
            if response.choices:
                message = response.choices[0].message
                content = message.content if message.content else ""
                # 开始解析reasoning_content，需要注意不同供应商对于思考过程的存放位置，如果没有则返回空字符串
                # 阿里云SDK会将不符合OpenAI规范的额外key，放在名为model_extra的字典内
                if message.model_extra:
                    reasoning_content = message.model_extra.get("reasoning_content", "")
                elif hasattr(message, "get"):
                    reasoning_content = message.get("reasoning_content", "")
                else:
                    reasoning_content = ""
                print(f"LLM返回内容: {content}，reasoning_content：{reasoning_content}")
                return content, reasoning_content

            return "", ""

        except Exception as e:
            print(f"LLM调用出错: {str(e)}")
            traceback.print_exc()
            return "", ""

    # def chat(self, messages, debug=False):
    #     """
    #     该函数在类初始化时会被替换成OpenAI或HUOSHAN对应的函数
    #     """
    #     return "", ""

    def huoshan_chat_stream(self, messages, debug=False):
        client = Ark(api_key=HUOSHAN_API_KEY)

        print(f"请求{self.model_name}: {messages}")
        stream = self.client.chat.completions.create(
            model=DOUBAO_MODEL_NAME,
            messages=messages,
            stream=True
        )
        reasoning_content = ""
        full_content = ""
        for chunk in stream:
            if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                reasoning_content += chunk.choices[0].delta.reasoning_content
                if debug:
                    print(chunk.choices[0].delta.reasoning_content, end="")
            if chunk.choices:
                full_content += chunk.choices[0].delta.content
                if debug:
                    print(chunk.choices[0].delta.content, end="")
        print(f"{self.model_name}返回内容: {full_content}。\n---\n思考过程：{reasoning_content}\n")
        return full_content, reasoning_content

    def openai_compatible_chat_stream(self, messages, debug=False):
        try:
            print(f"请求{self.model_name}: {messages}")
            if self.model_name == HUNYUAN_MODEL_NAME:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stream=True,
                    extra_body={
                        "enable_enhancement": True,
                        "enable_deep_search":True
                    }
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stream=True
                )

            full_content = ""
            reasoning_content = ""
            if debug:
                print("流式输出内容为：")
            for chunk in response:
                # 如果stream_options.include_usage为True，则最后一个chunk的choices字段为空列表，需要跳过（可以通过chunk.usage获取 Token 使用量）
                if chunk.choices:
                    # print(".")
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                        if debug:
                            print(delta.reasoning_content, end="", flush=True)
                        reasoning_content += delta.reasoning_content

                    if chunk.choices[0].delta.content:
                        full_content += chunk.choices[0].delta.content
                        if debug:
                            print(chunk.choices[0].delta.content, end="", flush=True)
            print(f"{self.model_name}返回内容: {full_content}。\n---\n思考过程：{reasoning_content}\n")

            return full_content, reasoning_content

        except Exception as e:
            print(f"LLM调用出错: {str(e)}")
            traceback.print_exc()
            return "", ""


def simple_example():
    llm = LLMClient(model_name=DEEPSEEK_MODEL_NAME)
    messages = [
        {"role": "user", "content": "你好,我是一名高中生，请介绍一下文理分科应该怎么选。"}
    ]
    response = llm.chat(messages)
    print(f"响应: {response}")


def stream_output_example():
    llm = LLMClient(model_name=HUNYUAN_MODEL_NAME)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好,我是一名高中生，请介绍一下文理分科应该怎么选。"}
    ]
    response = llm.chat(messages, debug=True)
    print(f"响应: {response}")


# 使用示例
if __name__ == "__main__":
    stream_output_example()
