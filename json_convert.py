import os
import json


def convert_game_record_to_chinese_text(json_file_path, including_reasoning=False):
    """将游戏记录转换为中文可读风格文本"""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        game_data = json.load(f)

    game_id = game_data["game_id"]
    player_names = game_data["player_names"]
    rounds = game_data["rounds"]
    winner = game_data.get("winner", "游戏仍在进行")

    # 开头介绍
    text = f"游戏编号：{game_id}\n"
    text += f"玩家列表：{', '.join(player_names)}\n\n"
    text += "════════════════════════════\n"
    text += "         游戏开始\n"
    text += "════════════════════════════\n\n"

    for round_record in rounds:
        # 每轮开始的分隔符
        text += "────────────────────────────\n"
        text += f"第 {round_record['round_id']} 轮\n"
        text += "────────────────────────────\n"
        text += f"本轮玩家：{', '.join(round_record['round_players'])}\n"
        text += f"本轮由 {round_record['starting_player']} 先开始。\n\n"

        # 记录玩家间的意见
        active_players = round_record["round_players"]
        for player_name, opinions in round_record["player_opinions"].items():
            # 只显示本轮参与的玩家的意见
            if player_name in active_players:
                text += f"{player_name} 对其他玩家的看法：\n"
                for other_player, opinion in opinions.items():
                    if other_player in active_players:
                        text += f"  - {other_player}: {opinion}\n"
                text += "\n"

        text += "开始发牌...\n\n"
        text += f"本轮目标牌：{round_record['target_card']}\n"

        # 添加player_initial_states的部分
        if "player_initial_states" in round_record:
            text += "各玩家初始状态：\n"
            for player_state in round_record["player_initial_states"]:
                player_name = player_state["player_name"]
                bullet_pos = player_state["bullet_position"]
                gun_pos = player_state["current_gun_position"]
                initial_hand = ", ".join(player_state["initial_hand"])

                text += f"{player_name}：\n"
                text += f"  - 子弹位置：{bullet_pos}\n"
                text += f"  - 当前弹仓位置：{gun_pos}\n"
                text += f"  - 初始手牌：{initial_hand}\n\n"

        text += "----------------------------------\n"
        for action in round_record["play_history"]:
            # 从 JSON 中获取玩家表现，并结合出牌行为
            text += f"轮到 {action['player_name']} 出牌\n"
            # 从 JSON 中获取玩家表现，并结合出牌行为
            text += f"{action['player_name']} {action['behavior']}\n"
            # 在一行显示出牌和剩余手牌，并在括号中显示目标牌
            text += f"出牌：{'、'.join(action['played_cards'])}，剩余手牌：{'、'.join(action['remaining_cards'])} (目标牌：{round_record['target_card']})\n"
            text += f"出牌理由：{action['play_reason']}\n"
            # 补充推理过程
            if including_reasoning:
                if len(action['play_thinking'])==0:
                    text += f"推理过程：该模型无推理过程或此次回答无推理过程\n\n"
                else:
                    action['play_thinking'] = action['play_thinking'].replace('\n\n', '\n')
                    text += f"推理过程：\n{action['play_thinking']}\n\n"

            # 不论是否质疑，都显示质疑原因，将理由放在下一行
            if action['was_challenged']:
                text += f"{action['next_player']} 选择质疑\n"
                text += f"质疑理由：{action['challenge_reason']}\n"
            else:
                text += f"{action['next_player']} 选择不质疑\n"
                text += f"不质疑理由：{action['challenge_reason']}\n"
            if including_reasoning:
                # 补充推理过程
                action['challenge_thinking'] = action['challenge_thinking'].replace('\n\n', '\n')
                if len(action['challenge_thinking'])==0:
                    text += f"推理过程：该模型无推理过程或此次回答无推理过程\n\n"
                else:
                    text += f"推理过程：\n{action['challenge_thinking']}\n\n"

            # 质疑过程
            if action['was_challenged']:
                if action['challenge_result']:
                    text += f"质疑结果：成功，{action['player_name']} 被揭穿。\n"
                else:
                    text += f"质疑结果：失败，{action['next_player']} 被惩罚。\n"
            text += "\n----------------------------------\n"

        # 记录射击结果
        if round_record['round_result']:
            result = round_record['round_result']
            text += f"射击结果：\n"

            if result["bullet_hit"]:
                text += f"子弹命中，{result['shooter_name']} 死亡。\n"
            else:
                text += f"子弹未击中，{result['shooter_name']} 幸免于难。\n"

            text += "\n"

    # 游戏结束分隔符和赢家宣布
    text += "\n════════════════════════════\n"
    text += "         游戏结束\n"
    text += "════════════════════════════\n\n"

    # 突出显示最终赢家
    text += "★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★\n"
    text += f"    最终胜利者：{winner}\n"
    text += "★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★\n"

    return text


def process_game_records(input_directory, output_directory, including_reasoning=False):
    """处理目录中的所有游戏记录 JSON 文件，生成可读风格的 TXT 文件到指定输出目录。
    增加including_reasoning入参，表示是否将json中的推理过程（reasoning_content）输出到txt文件中"""
    # 确保输出目录存在
    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            json_file_path = os.path.join(input_directory, filename)
            txt_file_path = os.path.join(output_directory, os.path.splitext(filename)[0] + '.txt')

            print(f"正在处理 {filename}...")
            game_text = convert_game_record_to_chinese_text(json_file_path, including_reasoning)

            with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(game_text)
            print(f"已生成：{txt_file_path}")


if __name__ == '__main__':
    game_records_directory = 'game_records_xiaozi_no_random'
    output_directory = 'converted_game_records_xiaozi_no_random'  # 新的输出目录
    process_game_records(game_records_directory, output_directory, including_reasoning=True)
