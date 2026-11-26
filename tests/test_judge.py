from src.judge import has_fully_crossed_goal_line
from src.judge import Scoreboard


def test_puck_trailing_edge_touching_goal_line():
    # 퍽이 골문 정중앙에서 좌표가 커지는 방향으로 이동한다.
    # 골라인은 100mm, 퍽 중심은 110mm, 반지름은 10mm다.
    crossed = has_fully_crossed_goal_line(
        center_mm=110,
        radius_mm=10,
        goal_line_mm=100,
    )

    assert crossed is False
    
def test_same_goal_counts_once_across_two_frames():
    board = Scoreboard(player_score=1, robot_score=1)

    # 첫 프레임. 퍽 전체가 로봇 골문으로 들어갔다.
    board.observe_goals(in_player_goal=False, in_robot_goal=True)
    assert (board.player_score, board.robot_score) == (2, 1)

    # 다음 프레임. 서브 전이고, 같은 퍽이 아직 같은 골문에 있다.
    board.observe_goals(in_player_goal=False, in_robot_goal=True)
    assert (board.player_score, board.robot_score) == (2, 1)
    
def test_puck_trailing_edge_past_goal_line():
    # 오른쪽 골문으로 들어가는 상황이다. x좌표는 오른쪽으로 갈수록 커진다.
    # 골라인의 위치는 x=100mm, 퍽 중심의 위치는 x=111mm다.
    # 반지름이 10mm이므로 마지막 가장자리도 x=101mm까지 지나갔다.
    crossed = has_fully_crossed_goal_line(
        center_mm=111,
        radius_mm=10,
        goal_line_mm=100,
    )

    assert crossed is True

def test_conceding_side_serves_and_next_rally_can_score():
    board = Scoreboard(player_score=1, robot_score=1)

    # 사람이 득점한다. 실점한 로봇에게 서브권이 간다.
    board.observe_goals(in_player_goal=False, in_robot_goal=True)
    assert (board.player_score, board.robot_score) == (2, 1)
    assert board.next_server == "robot"

    # 사람이 먼저 시도해도 로봇의 서브권은 유지된다.
    assert board.serve("player") is False
    assert board.next_server == "robot"
    assert board.rally_active is False

    # 로봇이 서브하면 점수를 유지한 채 새 랠리가 시작된다.
    assert board.serve("robot") is True
    assert board.rally_active is True
    assert (board.player_score, board.robot_score) == (2, 1)

    # 새 랠리에서 퍽이 사람 골문에 들어간다.
    board.observe_goals(in_player_goal=True, in_robot_goal=False)
    assert (board.player_score, board.robot_score) == (2, 2)
    assert board.next_server == "player"
    
def test_third_point_ends_game_and_blocks_further_play():
    board = Scoreboard(player_score=2, robot_score=2)

    # 사람이 결승점을 넣는다.
    board.observe_goals(in_player_goal=False, in_robot_goal=True)
    assert (board.player_score, board.robot_score) == (3, 2)
    assert board.winner == "player"
    assert board.rally_active is False
    assert board.next_server is None

    # 실점한 로봇도 끝난 경기를 서브로 재개할 수 없다.
    assert board.serve("robot") is False

    # 종료 후 반대쪽 골문에서 퍽이 감지돼도 최종 점수는 유지된다.
    board.observe_goals(in_player_goal=True, in_robot_goal=False)
    assert (board.player_score, board.robot_score) == (3, 2)