# Liars Bar LLM Mod

一个由大语言模型驱动的AI版骗子酒馆对战框架，原始项目为[liars-bar-llm](https://github.com/LYiHub/liars-bar-llm/blob/main/game.py)。

## 修改点
### 模型配置
本项目主要针对中文大模型进行测试，添加了火山引擎的兼容内容，相关依赖包可以参考`requirements.txt`文件。同时，添加了流式输出，降低大模型响应超时的概率，同时对LLM的配置文件做了一些修改，通过环境变量来配置API_KEY，详情可查看`llm_client.py`文件。

### 提示词变化
对原项目的提示词做了一定的修改，添加了明确的Markdown风格的段落标识和列表符号，同时重点强调了模型的输出格式、json结构体内key的名称。

## 文件结构

程序主要分为两部分，游戏主体和分析工具

### 游戏主体

`game.py` 骗子酒馆游戏主程序

`player.py` 参与游戏的LLM智能体

`game_record.py` 用于保存和提取游戏记录

`llm_client.py` 用于配置模型接口和发起LLM请求

`multi_game_runner.py` 用于批量运行多轮游戏

### 分析工具

`game_analyze.py` 用于统计所有对局数据

`player_matchup_analyze.py` 用于提取互为对手的AI间的对局记录进行分析

`json_convert.py` 用于将json游戏记录转为可读文本

## 使用方法

### 运行

完成项目配置后，在`game.py`和`multi_game_runner.py`主程序入口的`player_configs`中设置正确的模型名称

运行单局游戏：
```
python game.py
```

运行多局游戏：
```
python multi_game_runner.py -n 10
```
在`-n`后指定你希望运行的游戏局数，默认为10局

### 分析

游戏记录会以json形式保存在目录下的`game_records`文件夹中

将json文件转为可读性更强的文本格式，转换后的文件会保存在目录下的`converted_game_records`文件夹中

```
python json_convert.py
```

提取所有游戏中AI之间两两对决的对局，转换后的文件会保存在目录下的`matchup_records`文件夹中

```
python player_matchup_analyze.py
```

统计并打印所有的对局数据

```
python game_analyze.py
```

