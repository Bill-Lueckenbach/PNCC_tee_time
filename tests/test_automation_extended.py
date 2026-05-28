"""Extended unit tests for automation.py.

Tests for main() orchestration and additional argparse scenarios.
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from PNCC_tee_time import automation


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


class TestMain:
    """Tests for main() orchestration function."""

    @patch("PNCC_tee_time.automation.settings.setup_logging")
    @patch("PNCC_tee_time.automation.argparse_setup")
    def test_main_calls_setup_logging(self, mock_argparse_setup, mock_setup_logging):
        """Should call setup_logging to configure logging."""
        # Arrange
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = argparse.Namespace(
            tee_date="today",
            tee_time="8am",
            players=["Lueckenbach, Bill"]
        )
        mock_argparse_setup.return_value = mock_parser

        # Act
        try:
            automation.main()
        except (ValueError, SystemExit):
            # main() may raise or exit; we just want to verify setup_logging was called
            pass

        # Assert
        mock_setup_logging.assert_called_once()

    @patch("PNCC_tee_time.automation.settings.setup_logging")
    @patch("PNCC_tee_time.automation.argparse_setup")
    def test_main_calls_argparse_setup(self, mock_argparse_setup, mock_setup_logging):
        """Should create and use argument parser."""
        # Arrange
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = argparse.Namespace(
            tee_date="today",
            tee_time="8am",
            players=["Lueckenbach, Bill"]
        )
        mock_argparse_setup.return_value = mock_parser

        # Act
        try:
            automation.main()
        except (ValueError, SystemExit):
            pass

        # Assert
        mock_argparse_setup.assert_called_once()
        mock_parser.parse_args.assert_called_once()

    @patch("PNCC_tee_time.automation.logger")
    @patch("PNCC_tee_time.automation.settings.setup_logging")
    @patch("PNCC_tee_time.automation.argparse_setup")
    def test_main_logs_parsed_arguments(
        self, mock_argparse_setup, mock_setup_logging, mock_logger
    ):
        """Should log the parsed command line arguments."""
        # Arrange
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = argparse.Namespace(
            tee_date="tomorrow",
            tee_time="9am",
            players=["Doe, Jane"]
        )
        mock_argparse_setup.return_value = mock_parser

        # Act
        try:
            automation.main()
        except (ValueError, SystemExit):
            pass

        # Assert
        # Verify that a debug log was made with the parsed arguments
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        assert len(debug_calls) >= 1

    @patch("PNCC_tee_time.date_time_utils.get_tee_date")
    @patch("PNCC_tee_time.automation.settings.setup_logging")
    @patch("PNCC_tee_time.automation.argparse_setup")
    def test_main_calls_get_tee_date(
        self, mock_argparse_setup, mock_setup_logging, mock_get_tee_date
    ):
        """Should parse the tee_date argument."""
        # Arrange
        import datetime as dt
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = argparse.Namespace(
            tee_date="tomorrow",
            tee_time="8am",
            players=["Lueckenbach, Bill"]
        )
        mock_argparse_setup.return_value = mock_parser
        mock_get_tee_date.return_value = dt.date.today() + dt.timedelta(days=1)

        # Act
        try:
            automation.main()
        except (ValueError, SystemExit):
            pass

        # Assert
        # Verify get_tee_date was called with the parsed tee_date string
        mock_get_tee_date.assert_called()


# ---------------------------------------------------------------------------
# MaxPlayersAction
# ---------------------------------------------------------------------------


class TestMaxPlayersActionExtended:
    """Extended tests for MaxPlayersAction argparse custom action."""

    def test_max_players_action_handles_none_values(self):
        """Should handle None values gracefully."""
        # Arrange
        parser = argparse.ArgumentParser()
        parser.add_argument("players", nargs="*", action=automation.MaxPlayersAction)
        namespace = argparse.Namespace()

        action = automation.MaxPlayersAction([], "players")

        # Act
        action(parser, namespace, None)

        # Assert
        assert namespace.players == []

    def test_max_players_action_converts_single_string_to_list(self):
        """Should convert a single string into a list with one element."""
        # Arrange
        parser = argparse.ArgumentParser()
        parser.add_argument("players", nargs="*", action=automation.MaxPlayersAction)
        namespace = argparse.Namespace()
        action = automation.MaxPlayersAction([], "players")

        # Act
        action(parser, namespace, "Lueckenbach, Bill")

        # Assert
        assert namespace.players == ["Lueckenbach, Bill"]

    def test_max_players_action_preserves_list_input(self):
        """Should preserve list input as-is."""
        # Arrange
        parser = argparse.ArgumentParser()
        parser.add_argument("players", nargs="*", action=automation.MaxPlayersAction)
        namespace = argparse.Namespace()
        action = automation.MaxPlayersAction([], "players")
        players_list = ["Lueckenbach, Bill", "Doe, Jane"]

        # Act
        action(parser, namespace, players_list)

        # Assert
        assert namespace.players == players_list

    def test_max_players_action_rejects_more_than_four_players(self):
        """Should reject more than 4 players with parser.error()."""
        # Arrange
        parser = argparse.ArgumentParser()
        parser.add_argument("players", nargs="*", action=automation.MaxPlayersAction)
        namespace = argparse.Namespace()
        action = automation.MaxPlayersAction([], "players")
        five_players = [f"Player {i}" for i in range(1, 6)]

        # Act / Assert
        with pytest.raises(SystemExit):
            action(parser, namespace, five_players)

    def test_max_players_action_accepts_exactly_four_players(self):
        """Should accept exactly 4 players."""
        # Arrange
        parser = argparse.ArgumentParser()
        parser.add_argument("players", nargs="*", action=automation.MaxPlayersAction)
        namespace = argparse.Namespace()
        action = automation.MaxPlayersAction([], "players")
        four_players = ["Lueckenbach, Bill", "Doe, Jane", "Smith, Alex", "Jones, Chris"]

        # Act
        action(parser, namespace, four_players)

        # Assert
        assert namespace.players == four_players

    def test_max_players_action_accepts_fewer_than_four_players(self):
        """Should accept fewer than 4 players."""
        # Arrange
        parser = argparse.ArgumentParser()
        parser.add_argument("players", nargs="*", action=automation.MaxPlayersAction)
        namespace = argparse.Namespace()
        action = automation.MaxPlayersAction([], "players")
        two_players = ["Lueckenbach, Bill", "Doe, Jane"]

        # Act
        action(parser, namespace, two_players)

        # Assert
        assert namespace.players == two_players

    def test_max_players_action_accepts_single_player(self):
        """Should accept a single player."""
        # Arrange
        parser = argparse.ArgumentParser()
        parser.add_argument("players", nargs="*", action=automation.MaxPlayersAction)
        namespace = argparse.Namespace()
        action = automation.MaxPlayersAction([], "players")

        # Act
        action(parser, namespace, "Lueckenbach, Bill")

        # Assert
        assert namespace.players == ["Lueckenbach, Bill"]

    def test_max_players_action_uses_dest_attribute(self):
        """Should set the value on the namespace using the dest attribute."""
        # Arrange
        parser = argparse.ArgumentParser()
        namespace = argparse.Namespace()
        # For positional arguments, the first arg is the dest name
        action = automation.MaxPlayersAction([], "players")

        # Act
        action(parser, namespace, ["Smith, Alex"])

        # Assert
        assert namespace.players == ["Smith, Alex"]
