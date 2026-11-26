def has_fully_crossed_goal_line(
    *, center_mm: float, radius_mm: float, goal_line_mm: float
) -> bool:
    """오른쪽 골문 안에서 퍽 전체가 골라인을 지났는지 판정한다.

    center_mm과 goal_line_mm은 같은 원점에서 오른쪽으로 잰 x좌표다.
    radius_mm은 퍽의 반지름이다. 모든 값의 단위는 mm다.
    """
    left_edge_mm = center_mm - radius_mm
    return left_edge_mm > goal_line_mm

from dataclasses import dataclass


@dataclass
class Scoreboard:
    player_score: int = 0
    robot_score: int = 0
    rally_active: bool = True
    next_server: str | None = None

    def observe_goals(
        self, *, in_player_goal: bool, in_robot_goal: bool
    ) -> None:
        """한 프레임의 골문 판정 결과를 점수판에 반영한다."""
        if not self.rally_active or self.winner is not None:
            return

        if in_robot_goal:
            self.player_score += 1
            self.next_server = "robot"
        elif in_player_goal:
            self.robot_score += 1
            self.next_server = "player"
        else:
            return

        self.rally_active = False
        if self.winner is not None:
            self.next_server = None
        
    def serve(self, side: str) -> bool:
        """실점한 쪽의 서브를 받아들이면 새 랠리를 시작한다."""
        if self.winner is not None or self.rally_active or side != self.next_server:
            return False

        self.next_server = None
        self.rally_active = True
        return True
    @property
    def winner(self) -> str | None:
        if self.player_score >= 3:
            return "player"
        if self.robot_score >= 3:
            return "robot"
        return None