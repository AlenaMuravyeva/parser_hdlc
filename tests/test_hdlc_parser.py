"""Tests HDLC parser."""
import StringIO
import pytest
from pars_hdlc import parser

# pylint: disable=redefined-outer-name
@pytest.fixture()
def pars():
    """Create fixture, which create new instance Parser."""
    parser_object = parser.Parser()
    return parser_object


@pytest.mark.parametrize("test_input,expected", [
    (
        "7ea0586103300751e6e700614aa109060760857405080101a2030201"
        "00a305a10302010e88020780890760857405080202aa1280106162636"
        "465666768696a6b6c6d6e6f70be10040e0800065f1f040000181d0164000718d07e",
        parser.Message(
            flag='7e',
            frame_format=parser.FrameFormat(
                frame_len=88,
                fragmention_bit='False',
                format_type=3,
            ),
            dest_addr='61',
            scr_addr='03',
            control=parser.Control(
                lsb=0,
                command_response='I',
                recive=32,
                send=0,
                poll_finall=1,
            ),
            hcs=20743,
            information='e6e700614aa109060760857405080101a203020100a305a103020'
                        '10e88020780890760857405080202aa1280106162636465666768'
                        '696a6b6c6d6e6f70be10040e0800065f1f040000181d01640007',
            fcs=53272,
            flag_end='7e',
        ),
    ),
    (
        "7ea00703413142e27e",
        parser.Message(
            flag='7e',
            frame_format=parser.FrameFormat(
                frame_len=7,
                fragmention_bit='False',
                format_type=3,
            ),
            dest_addr='03',
            scr_addr='41',
            control=parser.Control(
                lsb=1,
                command_response='RR',
                recive=32,
                send=0,
                poll_finall=1,
            ),
            hcs=57922,
            information=None,
            fcs=None,
            flag_end='7e',
        ),
    ),
    (
        "7ea00703415144817e",
        parser.Message(
            flag='7e',
            frame_format=parser.FrameFormat(
                frame_len=7,
                fragmention_bit='False',
                format_type=3,
            ),
            dest_addr='03',
            scr_addr='41',
            control=parser.Control(
                lsb=1,
                command_response='RR',
                recive=64,
                send=0,
                poll_finall=1,
            ),
            hcs=33092,
            information=None,
            fcs=None,
            flag_end='7e',
        ),
    ),
    (
        "7ea00703417146a07e",
        parser.Message(
            flag='7e',
            frame_format=parser.FrameFormat(
                frame_len=7,
                fragmention_bit='False',
                format_type=3,
            ),
            dest_addr='03',
            scr_addr='41',
            control=parser.Control(
                lsb=1,
                command_response='RR',
                recive=96,
                send=0,
                poll_finall=1,
            ),
            hcs=41030,
            information=None,
            fcs=None,
            flag_end='7e',
        ),
    ),
    (
        "7ea0200361931b9f8180140502080006020800070400000007080400000007b3c67e",
        parser.Message(
            flag='7e',
            frame_format=parser.FrameFormat(
                frame_len=32,
                fragmention_bit='False',
                format_type=3,
            ),
            dest_addr='03',
            scr_addr='61',
            control=parser.Control(
                lsb=1,
                command_response='SNRM',
                recive=128,
                send=2,
                poll_finall=1,
            ),
            hcs=40731,
            information='8180140502080006020800070400000007080400000007',
            fcs=50867,
            flag_end='7e',
        ),
    ),
    (
        "7ea01e61031e56c4e6e700c4018100090c07e10619ff0d2c2fff80000048f27e",
        parser.Message(
            flag='7e',
            frame_format=parser.FrameFormat(
                frame_len=30,
                fragmention_bit='False',
                format_type=3,
            ),
            dest_addr='61',
            scr_addr='03',
            control=parser.Control(
                lsb=0,
                command_response='I',
                recive=0,
                send=14,
                poll_finall=1,
            ),
            hcs=50262,
            information='e6e700c4018100090c07e10619ff0d2c2fff800000',
            fcs=62024,
            flag_end='7e',
        ),
    ),
    (
        "7ea011610330d3bee6e700c70181010052ab7e",
        parser.Message(
            flag='7e',
            frame_format=parser.FrameFormat(
                frame_len=17,
                fragmention_bit='False',
                format_type=3,
            ),
            dest_addr='61',
            scr_addr='03',
            control=parser.Control(
                lsb=0,
                command_response='I',
                recive=32,
                send=0,
                poll_finall=1,
            ),
            hcs=48851,
            information='e6e700c701810100',
            fcs=43858,
            flag_end='7e',
        ),
    ),
])
def test_get_payload(pars, test_input, expected):
    """Checking decoding HDLC frame."""
    assert pars.get_payload(test_input) == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        "7ea011610330d3bee6e700c70181010052ab7e",
        "7ea011610330d3bee6e700c70181010052ab7e",

    ),
])
def test_transformation_to_bytes(pars, test_input, expected):
    """Checking assignment value field 'raw_frama'."""
    pars.transformation_to_bytes(test_input)
    assert pars.raw_frame == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        StringIO.StringIO("7e".decode('hex')),
        "7e"
    ),
])
def test_get_flag(pars, test_input, expected):
    """Checking the return value 'flag'"""
    # pylint: disable=protected-access
    flag = pars._get_flag(test_input)
    assert flag == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        40992,
        32
    ),
])
def test_get_len(pars, test_input, expected):
    """Checking the return value 'lenght' of the frame format field."""
    # pylint: disable=protected-access
    field_len = pars._get_len(test_input)
    assert field_len == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        40997,
        'False'
    ),
])
def test_get_fragmentation_bit(pars, test_input, expected):
    """Checking the return value 'segmentation' of the frame format field."""
    # pylint: disable=protected-access
    status = pars._get_fragmentation_bit(test_input)
    assert status == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        40985,
        3
    ),
])
def test_get_type(pars, test_input, expected):
    """Checking the return value 'type' of the frame format field."""
    # pylint: disable=protected-access
    value_type = pars._get_type(test_input)
    assert value_type == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        StringIO.StringIO("a011".decode('hex')),
        {'fragmention_bit': 'False', 'frame_len': 17, 'format_type': 3}
    ),
])
def test_get_frame_format(pars, test_input, expected):
    """Checking the return value of the frame format field."""
    # pylint: disable=protected-access
    frame_format = pars._get_frame_format(test_input)
    assert frame_format == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        StringIO.StringIO("61".decode('hex')),
        '61'
    ),
])
def test_get_address(pars, test_input, expected):
    """Checking the return value the destination or source address."""
    # pylint: disable=protected-access
    address = pars._get_address(test_input)
    assert address == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        0x96,
        0
    ),
])
def test_get_lsb(pars, test_input, expected):
    """Checking the return value 'LSB' of the 'control' field."""
    # pylint: disable=protected-access
    lsb = pars._get_lsb(test_input)
    assert lsb == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        (0, 32, 0), 'I',
    ),
])
def test_define_type_field_control(pars, test_input, expected):
    """Checking the return value 'Type' of the 'control' field."""
    # pylint: disable=protected-access
    send, recive, lsb = test_input
    type_control = pars._define_type_field_control(send, recive, lsb)
    assert type_control == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        StringIO.StringIO("71".decode('hex')), {
            'command_response': 'RR',
            'send': 0,
            'recive': 96,
            'lsb': 1,
            'poll_finall': 1
        },
    ),
])
def test_get_controll(pars, test_input, expected):
    """Checking the return value of the 'control' field."""
    # pylint: disable=protected-access
    control = pars._get_control(test_input)
    assert control == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        48, 1,
    ),
])
def test_get_poll_fin(pars, test_input, expected):
    """Checking the return value 'poll/finall' of the 'control' field."""
    # pylint: disable=protected-access
    field_poll_fin_control = pars._get_poll_fin(test_input)
    assert field_poll_fin_control == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        48, 32,
    ),
])
def test_get_recive(pars, test_input, expected):
    """Checking the return value 'recive' of the 'control' field."""
    # pylint: disable=protected-access
    field_recive_control = pars._get_recive(test_input)
    assert field_recive_control == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        147, 2,
    ),
])
def test_get_send(pars, test_input, expected):
    """Checking the return value 'send' of the 'control' field."""
    # pylint: disable=protected-access
    field_send_control = pars._get_send(test_input)
    assert field_send_control == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        [40731, 'a020036193'.decode('hex'), "HCS"], None,
    ),
])
def test_validate_hcs_checksum(pars, test_input, expected):
    """Checking the correct value of the check amount "HCS"."""
    # pylint: disable=protected-access
    hcs, value, checksum_type = test_input
    return_value = pars._validate_checksum(hcs, value, checksum_type)
    assert return_value == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        [StringIO.StringIO("b3c6".decode('hex')), {
            'fragmention_bit': 'False',
            'frame_len': 32,
            'format_type': 3
        }
        ], 50867,
    ),
])
def test_get_fcs(pars, test_input, expected):
    """Checking the return value 'header check sequence'"""
    # pylint: disable=protected-access
    # pylint: disable=line-too-long
    srt_bytes, frame_format = test_input
    pars.raw_frame = "7ea0200361931b9f8180140502080006020800070400000007080400000007b3c67e"
    pars.counter_readed_bytes = 31
    value_fcs = pars._get_fcs(srt_bytes, frame_format)
    assert value_fcs == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        StringIO.StringIO("1b9f".decode('hex')), 40731,
    ),
])
def test_get_hcs(pars, test_input, expected):
    """Checking the return value 'frame check sequence'"""
    # pylint: disable=protected-access
    # pylint: disable=line-too-long
    pars.raw_frame = ("7ea0200361931b9f8180140502080006020800070400000007080400000007b3c67e")
    pars.counter_readed_bytes = 6
    value_fcs = pars._get_hcs(test_input)
    assert value_fcs == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        [
            StringIO.StringIO(
                "818014050208000602080007040000000708040000000"
                "7b3c67e".decode('hex')
            ),
            {
                'fragmention_bit': 'False',
                'frame_len': 32,
                'format_type': 3
            }
        ], "8180140502080006020800070400000007080400000007"
    ),
])
def test_get_information(pars, test_input, expected):
    """Checking the return value 'information'"""
    # pylint: disable=protected-access
    pars.counter_readed_bytes = 8
    str_bytes, frame_format = test_input
    value_information = pars._get_information(str_bytes, frame_format)
    assert value_information == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        {'fragmention_bit': 'False', 'frame_len': 32, 'format_type': 3}, None,
    ),
])
def test_validation_lenght(pars, test_input, expected):
    """Checking the correct value 'lenght' of the frame format."""
    # pylint: disable=protected-access
    pars.counter_readed_bytes = 33
    return_value = pars._validation_lenght(test_input)
    assert return_value == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        [
            50867,
            'a0200361931b9f818014050208000'
            '6020800070400000007080400000007'.decode('hex'),
            'FCS'
        ],
        None,
    ),
])
def test_validate_fcs__checksum(pars, test_input, expected):
    """Checking the correct value of the check amount "FCS"."""
    # pylint: disable=protected-access
    fcs, value, checksum_type = test_input
    return_value = pars._validate_checksum(fcs, value, checksum_type)
    assert return_value == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        {
            'flag': '7e',
            'frame_format': {
                'fragmention_bit': 'False', 'frame_len': 32, 'format_type': 3
            },
            'dest_address': '61',
            'scr_address': '03',
            'control': {
                'command_response': 'SNRM',
                'send': 2,
                'recive': 128,
                'lsb': 1,
                'poll_finall': 1
            },
            'hcs': 40731,
            'information': '8180140502080006020800070400000007080400000007',
            'fcs': 50867,
            'flag_end': '7e',
        },
        parser.Message(
            flag='7e',
            frame_format=parser.FrameFormat(
                frame_len=32,
                fragmention_bit='False',
                format_type=3,
            ),
            dest_addr='61',
            scr_addr='03',
            control=parser.Control(
                lsb=1,
                command_response='SNRM',
                recive=128,
                send=2,
                poll_finall=1,
            ),
            hcs=40731,
            information='8180140502080006020800070400000007080400000007',
            fcs=50867,
            flag_end='7e',
        ),
    ),
])
def test_construct_data_object(pars, test_input, expected):
    """Checking that the data object constracted correctly."""
    # pylint: disable=protected-access
    return_value = pars._construct_data_object(test_input)
    assert return_value == expected


@pytest.mark.parametrize("test_input", [
    (
        {'fragmention_bit': 'False', 'frame_len': 38, 'format_type': 3}
    ),
])
def test_raise_exception_validation_lenght(pars, test_input):
    """
    It is checked that an exception is created,
    when 'farne_len" is not correct
    """
    # pylint: disable=protected-access
    with pytest.raises(parser.LenghtError):
        pars.counter_readed_bytes = 33
        pars._validation_lenght(test_input)


@pytest.mark.parametrize("test_input", [
    (
        [
            50850,
            'a0200361931b9f818014050208000'
            '6020800070400000007080400000007'.decode('hex'),
            'FCS'
        ]
    ),
    (
        [
            4,
            'a0200361931b9f818014050208000'
            '6020800070400000007080400000007'.decode('hex'),
            'HCS'
        ]
    )
])
def test_raise_validate_checksum(pars, test_input):
    """
    It is checked that an exception is created,
    when 'checksum" is not correct
    """
    # pylint: disable=protected-access
    fcs, value, checksum_type = test_input
    with pytest.raises(parser.CheckSummError):
        pars._validate_checksum(fcs, value, checksum_type)
