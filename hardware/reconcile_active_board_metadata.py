#!/usr/bin/env python3
"""Apply only the approved Rev.1 title-block and general-status text update."""

from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


TITLE = "ESP32 + E220 carrier — Rev.1 controlled routing"
COMMENT = "POWER + 5V ROUTING REVIEWED / SIGNAL ROUTING INCOMPLETE / NOT FOR PRODUCTION"
TEXT_REPLACEMENTS = {
    "STAGE 8 — FUNCTIONAL PLACEMENT ONLY / NO ROUTING": (
        "REV.1 CONTROLLED ROUTING — POWER + 5V PASSED / SIGNAL ROUTING PENDING"
    ),
    "U1 EP=GND. THERMAL VIAS / SW-COPPER POLICY: LAYOUT REVIEW REQUIRED": (
        "TPS62133 BUCK CELL — REVIEWED RETAINED CHECKPOINT"
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=Path, required=True)
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    title_block = board.GetTitleBlock()
    title_block.SetTitle(TITLE)
    title_block.SetComment(0, COMMENT)

    replaced = set()
    for drawing in board.GetDrawings():
        if not isinstance(drawing, pcbnew.PCB_TEXT):
            continue
        text = drawing.GetText()
        if text in TEXT_REPLACEMENTS:
            drawing.SetText(TEXT_REPLACEMENTS[text])
            replaced.add(text)
    if replaced != set(TEXT_REPLACEMENTS):
        missing = sorted(set(TEXT_REPLACEMENTS) - replaced)
        raise RuntimeError(f"Missing expected status text: {missing}")

    pcbnew.SaveBoard(str(args.board), board)
    reloaded = pcbnew.LoadBoard(str(args.board))
    if reloaded.GetTitleBlock().GetTitle() != TITLE:
        raise RuntimeError("Title-block reload verification failed")
    if reloaded.GetTitleBlock().GetComment(0) != COMMENT:
        raise RuntimeError("Title-block comment reload verification failed")
    current_texts = {
        drawing.GetText() for drawing in reloaded.GetDrawings()
        if isinstance(drawing, pcbnew.PCB_TEXT)
    }
    expected = set(TEXT_REPLACEMENTS.values())
    if not expected <= current_texts:
        raise RuntimeError("General-status text reload verification failed")
    print("METADATA UPDATE PASS")


if __name__ == "__main__":
    main()
