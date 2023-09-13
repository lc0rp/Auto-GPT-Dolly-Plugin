import importlib
import os
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from autogpt.config.config import Config
from autogpt.workspace.workspace import Workspace


@pytest.fixture()
def vcr_cassette_dir(request):
    test_name = os.path.splitext(request.node.name)[0]
    return os.path.join("tests/Auto-GPT-test-cassettes", test_name)


@pytest.fixture()
def workspace_root(tmp_path: Path) -> Path:
    return tmp_path / "home/users/monty/auto_gpt_workspace"


@pytest.fixture()
def workspace(workspace_root: Path) -> Workspace:
    workspace_root = Workspace.make_workspace(workspace_root)
    return Workspace(workspace_root, restrict_to_workspace=True)


@pytest.fixture()
def config(mocker: MockerFixture, workspace: Workspace) -> Config:
    config = Config()

    # Do a little setup and teardown since the config object is a singleton
    mocker.patch.multiple(
        config,
        workspace_path=workspace.root,
        file_logger_path=workspace.get_path("file_logger.txt"),
    )
    yield config
    
@pytest.fixture
def default_dolly(config):
    """ Returns a default Dolly object"""
    from autogpt_dolly_plugin.dolly import Dolly
    return Dolly(
        name="Test Dolly",
        role="Assistant",
        goals=["Goal 1", "Goal 2"],
        continuous_mode=False,
        continuous_limit=5,
        ffm_ocean_traits=[5, 5, 3, 5, 1],
        character_attributes=["helpful", "encouraging", "accurate"],
    )


def test_format_goals_str(config):
    from autogpt_dolly_plugin.dolly import Dolly

    dolly = Dolly("test_name", "test_role", ["goal1", "goal2", "goal3"], False)
    formatted_goals = dolly.goals_as_str
    expected_output = """- goal1
- goal2
- goal3"""
    assert formatted_goals == expected_output


def test_clone_autogpt_without_optional_params(config):
    with patch("autogpt_dolly_plugin.AutoGPTDollyPlugin") as MockAutoGPTDollyPlugin:
        plugin = MockAutoGPTDollyPlugin.return_value
        plugin.separate_settings = False
        plugin.enable_new_terminal_experiment = True

        import autogpt_dolly_plugin.dolly

        importlib.reload(autogpt_dolly_plugin.dolly)

        from autogpt_dolly_plugin.dolly import Dolly

        with patch(
            "autogpt_dolly_plugin.dolly_manager.DollyManager.write_to_file"
        ) as mock_write_to_file:
            mock_write_to_file.return_value.exists.return_value = True
            Dolly.goals_as_str = MagicMock()
            Dolly._disperse_settings = MagicMock()
            Dolly._disperse_shell_process = MagicMock()
            Dolly.execute_shell_command = MagicMock()
            dolly = Dolly("test_name", "test_role", ["test_goals", "test_goals2"], False)
            dolly.disperse()
            dolly._disperse_settings.assert_called_once()
            dolly._disperse_shell_process.assert_called_once()


def test_clone_autogpt_with_personality(config):
    with patch("autogpt_dolly_plugin.AutoGPTDollyPlugin") as MockAutoGPTDollyPlugin:
        plugin = MockAutoGPTDollyPlugin.return_value
        plugin.separate_settings = True
        plugin.enable_new_terminal_experiment = True

        import autogpt_dolly_plugin.dolly

        importlib.reload(autogpt_dolly_plugin.dolly)

        from autogpt_dolly_plugin.dolly import Dolly

        with patch(
            "autogpt_dolly_plugin.dolly_manager.DollyManager.write_to_file"
        ) as mock_write_to_file:
            mock_write_to_file.return_value.exists.return_value = True
            Dolly._disperse_settings = MagicMock()
            Dolly._disperse_shell_process = MagicMock()
            dolly = Dolly(
                "test_name", "test_role", ["test_goals",], continuous_mode=False, ffm_ocean_traits="1,2,3,4,5"
            )
            dolly.disperse()
            dolly._disperse_settings.assert_called_once()
            dolly._disperse_shell_process.assert_called_once()


@pytest.fixture
def workspace_path(tmp_path):
    return tmp_path


SETTINGS_TEMPLATE_CONTENT = """
ai_goals:
<GOALS>
ai_name: <NAME>
ai_role: <ROLE>
"""

def test_dolly_initialization(default_dolly):
    assert default_dolly.name == "Test Dolly"
    assert default_dolly.role == "Assistant"
    assert default_dolly.goals == ["Goal 1", "Goal 2"]
    assert default_dolly.continuous_mode is False
    assert default_dolly.continuous_limit == 5
    assert default_dolly.ffm_ocean_traits == [5, 5, 3, 5, 1]
    assert default_dolly.character_attributes == ["helpful", "encouraging", "accurate"]


def test_dolly_properties(default_dolly):
    assert default_dolly.dispersed is False
    assert default_dolly.index is None
    assert default_dolly.goals_as_str == """- Goal 1
- Goal 2"""
    assert default_dolly.ffm_ocean_traits_as_str == "5,5,3,5,1"
    assert default_dolly.character_attributes_as_str == "helpful,encouraging,accurate"


def test_dolly_property_setters(default_dolly):
    with pytest.raises(ValueError, match="Cannot set process more than once."):
        default_dolly.process = 1234
        default_dolly.process = 5678

    with pytest.raises(ValueError, match="Cannot set index more than once."):
        default_dolly.index = 1
        default_dolly.index = 2

def test_dolly_property_setters_index_integer(default_dolly):
    with pytest.raises(ValueError, match="Index must be an integer."):
        default_dolly.index = "not an integer"