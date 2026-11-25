#!/usr/bin/env python3
"""Refill only the retained U4 diagnostic board copy."""

from pathlib import Path

import pcbnew


BOARD = Path(__file__).resolve().parent / "refilled-project" / "esp32-e220.kicad_pcb"
board = pcbnew.LoadBoard(str(BOARD))
if len(list(board.GetTracks())) != 260 or len(list(board.Zones())) != 11:
    raise RuntimeError("diagnostic copy inventory differs from the approved board")
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD), board)
