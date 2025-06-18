import importlib.machinery
import importlib.util
import os
import sys
import types
import pytest


def load_hand_module():
    # Create dummy modules for heavy dependencies so the Hand module can be imported
    for name in ["cv2", "mediapipe", "pyautogui"]:
        sys.modules.setdefault(name, types.ModuleType(name))

    pycaw_mod = types.ModuleType("pycaw.pycaw")

    class DummyAudioUtilities:
        @staticmethod
        def GetAllSessions():
            return []

    class DummyISimpleAudioVolume:
        pass

    pycaw_mod.AudioUtilities = DummyAudioUtilities
    pycaw_mod.ISimpleAudioVolume = DummyISimpleAudioVolume
    sys.modules.setdefault("pycaw.pycaw", pycaw_mod)
    main_pycaw = types.ModuleType("pycaw")
    main_pycaw.pycaw = pycaw_mod
    sys.modules.setdefault("pycaw", main_pycaw)

    path = os.path.join(os.path.dirname(__file__), os.pardir, "utils", "Hand.py")
    loader = importlib.machinery.SourceFileLoader("hand_module", path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


hand_module = load_hand_module()
Hand = hand_module.Hand


def dummy_hand():
    return Hand.__new__(Hand)


def test_angle_between_points_basic():
    hand = dummy_hand()
    coords = [(0, 0)] * 9 + [(0, -10)]
    angle = hand.angle_between_points(coords)
    assert angle == pytest.approx(90)


def test_angle_between_points_negative():
    hand = dummy_hand()
    coords = [(0, 0)] * 9 + [(0, 10)]
    angle = hand.angle_between_points(coords)
    assert angle == pytest.approx(-90)


def test_calculate_direction_up():
    hand = dummy_hand()
    coords = [(0, 0)] * 9 + [(0, -10)]
    assert hand.calculate_direction(coords) == "Up"


def test_calculate_direction_right():
    hand = dummy_hand()
    coords = [(0, 0)] * 9 + [(10, 0)]
    assert hand.calculate_direction(coords) == "Right"


def test_calculate_direction_down():
    hand = dummy_hand()
    coords = [(0, 0)] * 9 + [(0, 10)]
    assert hand.calculate_direction(coords) == "Down"


def test_calculate_direction_none():
    hand = dummy_hand()
    coords = [(0, 0)] * 9 + [(-10, 0)]
    assert hand.calculate_direction(coords) == "nenhuma das anteriores"
