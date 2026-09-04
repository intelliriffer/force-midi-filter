#!/usr/bin/env python3
"""
Test script for Force MIDI Filter
==================================
Tests all core functions: config loading, port matching, message filtering.
Run with: python test.py
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the script directory to path so we can import midifilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import midifilter


class TestMessageMapping(unittest.TestCase):
    """Test message type alias mapping."""

    def test_all_aliases_exist(self):
        """All expected aliases should be in the mapping."""
        expected = ["NOTE", "NOTE_OFF", "CC", "PC", "NOTE_PRESSURE", "AFTERTOUCH", "PITCHBEND"]
        for alias in expected:
            self.assertIn(alias, midifilter.MESSAGE_TYPE_MAP)

    def test_mido_types_mapped(self):
        """All aliases should map to valid MIDO types."""
        valid_mido_types = [
            "note_on", "note_off", "control_change", "program_change",
            "note_pressure", "aftertouch", "pitch_bend"
        ]
        for mido_type in midifilter.MESSAGE_TYPE_MAP.values():
            self.assertIn(mido_type, valid_mido_types)

    def test_note_maps_to_note_on(self):
        """NOTE should map to note_on."""
        self.assertEqual(midifilter.MESSAGE_TYPE_MAP["NOTE"], "note_on")

    def test_cc_maps_to_control_change(self):
        """CC should map to control_change."""
        self.assertEqual(midifilter.MESSAGE_TYPE_MAP["CC"], "control_change")


class TestConfigLoading(unittest.TestCase):
    """Test config.ini parsing."""

    def _create_test_config(self, content):
        """Helper to create a temporary config file and load it."""
        test_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(test_dir, "config.ini")

        # Read and backup original content
        original_content = None
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                original_content = f.read()

        # Write test content
        with open(config_path, "w") as f:
            f.write(content)

        try:
            config = midifilter.load_config(config_path, verbose=False)
            return config
        finally:
            # Restore original content if we had it
            if original_content is not None:
                with open(config_path, "w") as f:
                    f.write(original_content)
            else:
                os.remove(config_path)
    def test_load_basic_config(self):
        """Test loading a basic config with MIDI_PORT and channel rules."""
        content = """
[DEFAULT]
MIDI_PORT=TestDevice

[CH-1]
RULE=ALL

[CH-2]
RULE=BLOCK
"""
        config = self._create_test_config(content)
        self.assertEqual(config["midi_port"], "TestDevice")
        self.assertIn(0, config["channels"])
        self.assertIn(1, config["channels"])
        self.assertEqual(config["channels"][0]["type"], "all")
        self.assertEqual(config["channels"][1]["type"], "block")

    def test_load_allow_rules(self):
        """Test loading config with allow (specific message types)."""
        content = """
[DEFAULT]
MIDI_PORT=TestDevice

[CH-3]
RULE=CC,PC,NOTE
"""
        config = self._create_test_config(content)
        self.assertEqual(config["channels"][2]["type"], "allow")
        self.assertIn("CC", config["channels"][2]["messages"])
        self.assertIn("PC", config["channels"][2]["messages"])
        self.assertIn("NOTE", config["channels"][2]["messages"])

    def test_load_all_rule(self):
        """Test loading config with ALL rule."""
        content = """
[DEFAULT]
MIDI_PORT=TestDevice

[CH-5]
RULE=ALL
"""
        config = self._create_test_config(content)
        self.assertEqual(config["channels"][4]["type"], "all")

    def test_load_block_rule(self):
        """Test loading config with BLOCK rule."""
        content = """
[DEFAULT]
MIDI_PORT=TestDevice

[CH-6]
RULE=BLOCK
"""
        config = self._create_test_config(content)
        self.assertEqual(config["channels"][5]["type"], "block")

    def test_ignore_comments(self):
        """Test that comment lines are ignored."""
        content = """
[DEFAULT]
# This is a comment
MIDI_PORT=TestDevice
# Another comment

[CH-1]
# Inline comment
RULE=ALL
"""
        config = self._create_test_config(content)
        self.assertEqual(config["midi_port"], "TestDevice")
        self.assertEqual(config["channels"][0]["type"], "all")

    def test_invalid_channel_skipped(self):
        """Test that invalid channel numbers are skipped."""
        content = """
[DEFAULT]
MIDI_PORT=TestDevice

[CH-0]
RULE=BLOCK

[CH-17]
RULE=ALL

[CH-1]
RULE=CC
"""
        config = self._create_test_config(content)
        self.assertNotIn(17, config["channels"])
        self.assertNotIn(17, config["channels"])
        self.assertIn(0, config["channels"])

    def test_missing_midi_port_exits(self):
        """Test that missing MIDI_PORT causes exit."""
        content = """
[CH-1]
RULE=ALL
"""
        with patch('sys.exit') as mock_exit:
            self._create_test_config(content)
            mock_exit.assert_called()


class TestPortMatching(unittest.TestCase):
    """Test MIDI port wildcard matching."""

    @patch.object(midifilter, 'mido')
    def test_case_insensitive_match(self, mock_mido):
        """Test case-insensitive port matching."""
        midifilter.CASE_INSENSITIVE_PORT_MATCH = True
        mock_mido.get_input_names.return_value = [
            "Launchpad Mini",
            "LAUNCHKEY 61",
            "MIDI Keyboard"
        ]

        matched = midifilter.match_midi_ports("launchpad")
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0], "Launchpad Mini")

    @patch.object(midifilter, 'mido')
    def test_case_sensitive_match(self, mock_mido):
        """Test case-sensitive port matching."""
        midifilter.CASE_INSENSITIVE_PORT_MATCH = False
        mock_mido.get_input_names.return_value = [
            "Launchpad Mini",
            "LAUNCHPAD PRO",
            "launchkey 61"
        ]

        matched = midifilter.match_midi_ports("LAUNCHPAD")
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0], "LAUNCHPAD PRO")

    @patch.object(midifilter, 'mido')
    def test_wildcard_matches_multiple(self, mock_mido):
        """Test wildcard matching multiple ports."""
        midifilter.CASE_INSENSITIVE_PORT_MATCH = True
        mock_mido.get_input_names.return_value = [
            "AKAI Force",
            "AKAI MPK",
            "MIDI Keyboard"
        ]

        matched = midifilter.match_midi_ports("AKAI")
        self.assertEqual(len(matched), 2)
        self.assertIn("AKAI Force", matched)
        self.assertIn("AKAI MPK", matched)

    @patch.object(midifilter, 'mido')
    def test_no_match(self, mock_mido):
        """Test when no ports match."""
        midifilter.CASE_INSENSITIVE_PORT_MATCH = True
        mock_mido.get_input_names.return_value = [
            "MIDI Keyboard",
            "USB Audio Interface"
        ]

        matched = midifilter.match_midi_ports("Launchpad")
        self.assertEqual(len(matched), 0)


class TestMessageFiltering(unittest.TestCase):
    """Test the is_message_allowed function."""

    def _make_message(self, msg_type, channel=0, **kwargs):
        """Create a mock MIDI message."""
        msg = MagicMock()
        msg.type = msg_type
        msg.channel = channel
        for k, v in kwargs.items():
            setattr(msg, k, v)
        return msg

    def test_block_rule(self):
        """Test BLOCK rule blocks all messages."""
        rules = {1: {"type": "block"}}
        msg = self._make_message("note_on", channel=1)
        self.assertFalse(midifilter.is_message_allowed(msg, rules))

    def test_all_rule(self):
        """Test ALL rule passes all messages."""
        rules = {2: {"type": "all"}}
        msg = self._make_message("control_change", channel=2)
        self.assertTrue(midifilter.is_message_allowed(msg, rules))

    def test_allow_specific_types(self):
        """Test allow rule only passes specified types."""
        rules = {3: {"type": "allow", "messages": ["CC", "PC"]}}

        msg_cc = self._make_message("control_change", channel=3)
        msg_note = self._make_message("note_on", channel=3)
        msg_pc = self._make_message("program_change", channel=3)

        self.assertTrue(midifilter.is_message_allowed(msg_cc, rules))
        self.assertFalse(midifilter.is_message_allowed(msg_note, rules))
        self.assertTrue(midifilter.is_message_allowed(msg_pc, rules))

    def test_unspecified_channel_blocked(self):
        """Test that channels without rules are blocked."""
        rules = {1: {"type": "all"}}
        msg = self._make_message("note_on", channel=5)
        self.assertFalse(midifilter.is_message_allowed(msg, rules))

    def test_channel_pressure_message(self):
        """Test NOTE_PRESSURE message filtering."""
        rules = {4: {"type": "allow", "messages": ["NOTE_PRESSURE"]}}
        msg = self._make_message("note_pressure", channel=4)
        self.assertTrue(midifilter.is_message_allowed(msg, rules))

        msg_cc = self._make_message("control_change", channel=4)
        self.assertFalse(midifilter.is_message_allowed(msg_cc, rules))

    def test_pitch_bend_message(self):
        """Test PITCHBEND message filtering."""
        rules = {5: {"type": "allow", "messages": ["PITCHBEND"]}}
        msg = self._make_message("pitch_bend", channel=5)
        self.assertTrue(midifilter.is_message_allowed(msg, rules))

    def test_aftertouch_message(self):
        """Test AFTERTOUCH message filtering."""
        rules = {6: {"type": "allow", "messages": ["AFTERTOUCH"]}}
        msg = self._make_message("aftertouch", channel=6)
        self.assertTrue(midifilter.is_message_allowed(msg, rules))


class TestConfigPath(unittest.TestCase):
    """Test config file path resolution."""

    def test_config_in_same_dir(self):
        """Test that config path is in the same directory as the script."""
        script_dir = os.path.dirname(os.path.abspath(midifilter.__file__))
        expected = os.path.join(script_dir, "config.ini")
        self.assertEqual(midifilter.find_config_path(), expected)


class TestListPorts(unittest.TestCase):
    """Test port listing functionality."""

    @patch.object(midifilter, 'mido')
    @patch('builtins.print')
    def test_list_ports(self, mock_print, mock_mido):
        """Test that list_ports outputs port names."""
        mock_mido.get_input_names.return_value = [
            "MIDI Keyboard",
            "Launchpad Mini"
        ]
        midifilter.list_ports()
        mock_print.assert_called()


if __name__ == "__main__":
    print("Running Force MIDI Filter tests...")
    print("-" * 50)
    unittest.main(verbosity=2)
