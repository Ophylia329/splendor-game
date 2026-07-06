"""
贵族类 - 表示贵族版图
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class Noble:
    """
    贵族版图类

    属性:
        noble_id: 贵族唯一标识
        name: 贵族名称（可选）
        requirements: 需要的红利数量 {'white': 数量, 'blue': 数量, ...}
        points: 声望分数（固定为3分）
    """
    noble_id: int
    name: str
    requirements: Dict[str, int]
    points: int = 3  # 贵族固定提供3分

    def __post_init__(self):
        """初始化后验证数据"""
        assert self.points == 3, f"贵族必须提供3分声望，当前为{self.points}"
        assert all(count >= 0 for count in self.requirements.values()), \
            "贵族需求的红利数量不能为负数"

    def check_requirements(self, bonuses: Dict[str, int]) -> bool:
        """
        检查玩家是否满足贵族的红利需求

        参数:
            bonuses: 玩家拥有的红利 {'white': 数量, 'blue': 数量, ...}

        返回:
            bool: 是否满足需求
        """
        for color, required in self.requirements.items():
            if bonuses.get(color, 0) < required:
                return False
        return True

    def __repr__(self):
        return f"Noble(id={self.noble_id}, {self.name}, 3分)"
