import traceback
import random
from game import Game
from typing import Dict, List
import llm_client
import argparse

class MultiGameRunner:
    def __init__(self, player_configs: List[Dict[str, str]], num_games: int = 10,player_order_random=True):
        """初始化多局游戏运行器
        
        Args:
            player_configs: 玩家配置列表
            num_games: 要运行的游戏局数
        """
        self.player_configs = player_configs
        self.num_games = num_games
        if player_order_random:
            random.shuffle(self.player_configs)

    def run_games(self) -> None:
        """运行指定数量的游戏"""

        for game_num in range(1, self.num_games + 1):
            try:
                print(f"\n=== 开始第 {game_num}/{self.num_games} 局游戏 ===")

                # 创建并运行新游戏
                game = Game(self.player_configs)
                game.start_game()

                print(f"第 {game_num} 局游戏结束")
            except Exception as e:
                print(f"第 {game_num} 局游戏出错: {e}")
                traceback.print_exc()
                continue


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='运行多局AI对战游戏',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-n', '--num-games',
        type=int,
        default=10,
        help='要运行的游戏局数 (默认: 10)'
    )
    return parser.parse_args()

if __name__ == '__main__':
    # 解析命令行参数
    args = parse_arguments()
    
    # 配置玩家信息, 其中model为你通过API调用的模型名称
    player_configs = [
        {
            "name": llm_client.MODEL_NICKNAME_DB[llm_client.QWEN_MODEL_NAME],
            "model": llm_client.QWEN_MODEL_NAME
        },
        {
            "name": llm_client.MODEL_NICKNAME_DB[llm_client.QWEN_THINKING_MODEL_NAME],
            "model": llm_client.QWEN_THINKING_MODEL_NAME
        },
        {
            "name": llm_client.MODEL_NICKNAME_DB[llm_client.DEEPSEEK_MODEL_NAME],
            "model": llm_client.DEEPSEEK_MODEL_NAME
        },
        {
            "name": llm_client.MODEL_NICKNAME_DB[llm_client.DOUBAO_MODEL_NAME],
            "model": llm_client.DOUBAO_MODEL_NAME
        }
    ]

    # 创建并运行多局游戏
    runner = MultiGameRunner(player_configs, num_games=args.num_games)
    runner.run_games()