import importlib
import os
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch
import pytest


def test_format_goals_str():
    """ """
    from autogpt_dolly_plugin.dolly import Dolly

    formatted_goals = Dolly.format_goals_str('["goal1", "goal2", "goal3"]')
    expected_output = """- goal1
- goal2
- goal3"""
    assert formatted_goals == expected_output

    formatted_goals_no_brackets = Dolly.format_goals_str('"goal1", "goal2", "goal3"')
    assert formatted_goals_no_brackets == expected_output

    formatted_goals_single = Dolly.format_goals_str('"goal1"')
    single_goal_output = "- goal1"
    assert formatted_goals_single == single_goal_output

    assert Dolly.format_goals_str("incorrect_json_string") == "- incorrect_json_string"


def test_clone_autogpt_without_optional_params():
    with patch("autogpt_dolly_plugin.AutoGPTDollyPlugin") as MockAutoGPTDollyPlugin:
        plugin = MockAutoGPTDollyPlugin.return_value
        plugin.separate_settings = False
        plugin.enable_new_terminal_experiment = True

        import autogpt_dolly_plugin.dolly

        importlib.reload(autogpt_dolly_plugin.dolly)

        from autogpt_dolly_plugin.dolly import Dolly

        with patch(
            "autogpt_dolly_plugin.dolly.Dolly.write_to_file"
        ) as mock_write_to_file:
            mock_write_to_file.return_value.exists.return_value = True
            Dolly.format_goals_str = MagicMock()
            Dolly.create_settings_file = MagicMock()
            Dolly.execute_shell_command = MagicMock()
            Dolly.clone_autogpt("test_name", "test_role", "test_goals")
            Dolly.format_goals_str.assert_called_once_with("test_goals")
            Dolly.create_settings_file.assert_not_called()
            Dolly.execute_shell_command.assert_called_once()


def test_clone_autogpt_with_big5_personality():
    with patch("autogpt_dolly_plugin.AutoGPTDollyPlugin") as MockAutoGPTDollyPlugin:
        plugin = MockAutoGPTDollyPlugin.return_value
        plugin.separate_settings = True
        plugin.enable_new_terminal_experiment = True

        import autogpt_dolly_plugin.dolly

        importlib.reload(autogpt_dolly_plugin.dolly)

        from autogpt_dolly_plugin.dolly import Dolly

        with patch(
            "autogpt_dolly_plugin.dolly.Dolly.write_to_file"
        ) as mock_write_to_file:
            mock_write_to_file.return_value.exists.return_value = True
            Dolly.create_settings_file = MagicMock()
            Dolly.execute_shell_command = MagicMock()
            Dolly.clone_autogpt(
                "test_name", "test_role", "test_goals", big5_personality="1,2,3,4,5"
            )
            Dolly.create_settings_file.assert_called_once_with(
                "test_name",
                "test_role",
                "- test_goals",
                "1,2,3,4,5",
                "helpful,encouraging,accurate",
                ANY,
            )
            Dolly.execute_shell_command.assert_called_once()


@pytest.fixture
def workspace_path(tmp_path):
    return tmp_path


SETTINGS_TEMPLATE_CONTENT = """
ai_goals:
<GOALS>
ai_name: <NAME>
ai_role: <ROLE>
"""


def test_create_settings_file(workspace_path):
    # Inputs
    name = "example_name"
    role = "example_role"
    goals = "goal1, goal2"
    big5_personality = "3,3,3,3,3"
    attributes = "att1,att2"

    settings_template = workspace_path / "ai_settings_template.yaml"
    settings_template.write_text(SETTINGS_TEMPLATE_CONTENT)

    import autogpt_dolly_plugin.dolly

    importlib.reload(autogpt_dolly_plugin.dolly)

    from autogpt_dolly_plugin.dolly import Dolly

    with patch("autogpt_dolly_plugin.dolly.Dolly.write_to_file") as mock_write_to_file:
        mock_write_to_file.return_value.exists.return_value = True

        # Call the function under test
        new_settings_filepath = Dolly.create_settings_file(
            name, role, goals, big5_personality, attributes, workspace_path
        )

        # Assert that write_to_file was called
        mock_write_to_file.assert_called_once()
        assert isinstance(mock_write_to_file.call_args[0][0], Path)

        # Check if the content of the new settings file is correct
        content = mock_write_to_file.call_args[0][1]
        assert name in content
        assert role in content
        assert big5_personality in content
        assert attributes in content
        for goal in goals.split(","):
            assert goal.strip() in content
        for attribute in attributes.split(","):
            assert attribute.strip() in content

        # Check if the new settings filepath was returned
        assert new_settings_filepath == workspace_path / f"ai_settings_{name}.yaml"
