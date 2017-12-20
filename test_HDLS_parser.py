import pytest
import pars_hdlc


@pytest.mark.parametrize("test_input,expected", [
    ("7ea0586103300751e6e700614aa109060760857405080101a2030201"
     "00a305a10302010e88020780890760857405080202aa1280106162636"
     "465666768696a6b6c6d6e6f70be10040e0800065f1f040000181d0164000718d07e",
    pars_hdlc.Message(
        flag = 7e,
        frame_format = pars_hdlc.Field_frame_format(),
        dest_addr = 61
        scr_addr = 03
        control = pars_hdlc.Field_controll(),
        hcs = 7
        information = e6e700614aa109060760857405080101a203020100a305a10302010e88020780890760857405080202aa1280106162636465666768696a6b6c6d6e6f70be10040e0800065f1f040000181d01640007
        fcs = 6352
        flag_end = 7e
    )
    ),
])
def test_parser():
    parser = pars_hdlc.Parser()
    assert parced_msg(test_input) == expected
