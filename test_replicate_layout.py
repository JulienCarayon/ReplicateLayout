#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import pcbnew
import logging
import sys
import os
import compare_boards
from replicate_layout import Replicator


def update_progress(stage, percentage, message=None):
    print(stage)
    print(percentage)
    if message is not None:
        print(message)


def test_file(in_filename, test_filename, src_anchor_fp_reference, level, sheets, containing, remove):
    board = pcbnew.LoadBoard(in_filename)
    # get board information
    replicator = Replicator(board, update_progress)
    # get source footprint info
    src_anchor_fp = replicator.get_fp_by_ref(src_anchor_fp_reference)
    # have the user select replication level
    levels = src_anchor_fp.filename
    # get the level index from user
    index = levels.index(levels[level])
    # get list of sheets
    sheet_list = replicator.get_sheets_to_replicate(src_anchor_fp, src_anchor_fp.sheet_id[index])

    # get anchor footprints
    anchor_footprints = replicator.get_list_of_footprints_with_same_id(src_anchor_fp.fp_id)
    # find matching anchors to matching sheets
    ref_list = []
    for sheet in sheet_list:
        for fp in anchor_footprints:
            if fp.sheet_id == sheet:
                ref_list.append(fp.ref)
                break

    # get the list selection from user
    dst_sheets = [sheet_list[i] for i in sheets]

    # first get all the anchor footprints
    all_sheet_footprints = []
    for sheet in dst_sheets:
        all_sheet_footprints.extend(replicator.get_footprints_on_sheet(sheet))
    anchor_fp = [x for x in all_sheet_footprints if x.fp_id == src_anchor_fp.fp_id]
    if all(src_anchor_fp.fp.IsFlipped() == dst_mod.fp.IsFlipped() for dst_mod in anchor_fp):
        a = 2
    else:
        assert (2 == 3), "Destination anchor footprints are not on the same layer as source anchor footprint"

    # now we are ready for replication
    replicator.replicate_layout(src_anchor_fp, src_anchor_fp.sheet_id[0:index + 1], dst_sheets,
                                containing=containing, remove=remove, rm_duplicates=True,
                                tracks=True, zones=True, text=True, drawings=True, rep_locked=True)
    out_filename = test_filename.replace("test", "temp")
    pcbnew.SaveBoard(out_filename, board)

    return compare_boards.compare_boards(out_filename, test_filename)


class TestByRef(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "replicate_layout_test_project"))

    def test_inner(self):
        logger.info("Testing multiple hierarchy - inner levels")
        input_filename = 'replicate_layout_test_project.kicad_pcb'
        test_filename = input_filename.split('.')[0] + "_test_inner" + ".kicad_pcb"
        err = test_file(input_filename, test_filename, 'Q301', level=1, sheets=(1, 2), containing=False, remove=False)
        # self.assertEqual(err, 0, "inner levels failed")

    def test_inner_level(self):
        logger.info("Testing multiple hierarchy - inner levels source on a different hierarchical level")
        input_filename = 'replicate_layout_test_project.kicad_pcb'
        test_filename = input_filename.split('.')[0] + "_test_inner_alt" + ".kicad_pcb"
        err = test_file(input_filename, test_filename, 'Q1401', level=0, sheets=(2, 3), containing=False, remove=False)
        # self.assertEqual(err, 0, "inner levels from bottom failed")

    def test_outer(self):
        logger.info("Testing multiple hierarchy - outer levels")
        input_filename = 'replicate_layout_test_project.kicad_pcb'
        test_filename = input_filename.split('.')[0] + "_test_outter" + ".kicad_pcb"
        err = test_file(input_filename, test_filename, 'Q301', level=0, sheets=(0,1), containing=False, remove=False)
        # self.assertEqual(err, 0, "outer levels failed")


# for testing purposes only
if __name__ == "__main__":
    file_handler = logging.FileHandler(filename='replicate_layout.log', mode='w')
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging_level = logging.INFO

    logging.basicConfig(level=logging_level,
                        format='%(asctime)s %(name)s %(lineno)d:%(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        handlers=handlers
                        )

    logger = logging.getLogger(__name__)
    logger.info("Plugin executed on: " + repr(sys.platform))
    logger.info("Plugin executed with python version: " + repr(sys.version))
    logger.info("KiCad build version: " + str(pcbnew.GetBuildVersion()))

    unittest.main()