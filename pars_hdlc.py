
"""HDLC parser."""
import collections
import StringIO


class Message(
    collections.namedtuple(
        'HDLC',
        [
            'flag',
            'frame_format',
            'dest_addr',
            'scr_addr',
            'control',
            'hcs',
            'information',
            'fcs',
            'flag_end'
        ]
    )
):
    def __str__(self):
        string = 'flag:{}.\n frame_format:{}\n\r frame_len:{}\n\r '
        'fragmention_bit:{}\n\r format_type{}.\n dest_addr: {}.\n'
        'scr_addr:{}\n control:{}\n\r lsb:{}\n\r command_response:{}\n\r'
        'recive:{}\n\r send:{}\n\r poll_finall:{}.\n hcs:{}\n information:{}\n'
        'fcs:{}.\n flag_end:{]\n'.format(
            self.flag, self.frame_format, FieldFrameFormat.frame_len,
            FieldFrameFormat.fragmention_bit, self.dest_addr,
            self.scr_addr, self.control, FieldControll.lsb,
            FieldControll.command_response, FieldControll.recive,
            FieldControll.send, FieldControll.poll_finall, self.hcs,
            self.information, FieldControll.fcs, FieldControll.flag_end
        )
        return string


FieldFrameFormat = collections.namedtuple(
    'FrameFormat', [
        'frame_len',
        'fragmention_bit',
        'format_type'
    ]
)

FieldControll = collections.namedtuple(
    "Controll", [
        'lsb',
        'command_response',
        'recive',
        'send',
        'poll_finall'
    ]
)


class CheckSummError(Exception):
    """
    Exception raised, if hcs or fcs is not correct
    """
    pass


class Parser(object):
    """ HDLC parser"""
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        self.data = ''
        self.position = 0
        self.bytes = 0
        self.position_controll = 0
        self.position_hcs = 0
        self.position_info = 0
        self.position_fcs = 0
        self.position_flag_end = 0
        self.message = None

    def transformation_to_bytes(self, data):
        """Converts to byte string."""
        self.data = data
        file_bytes = StringIO.StringIO(self.data.decode('hex'))
        for byte in file_bytes:
            self.bytes = byte

    def _add_flag(self):
        """
        Extract the flags from Message
         """
        if self.position == 0 and self.bytes[0] == '7e'.decode('hex'):
            Message.flag = self.bytes[0].encode('hex')
            self.position += 1
        if self.position == 8:
            flag = self.bytes[self.position_flag_end]
            Message.flag_end = flag.encode('hex')
            self.message = Message

    def _get_len(self, value_frame):
        """
        Return frame length
        """
        bit_mask_lenght = 0x7FF
        field_frame_format_len = value_frame & bit_mask_lenght
        return field_frame_format_len

    def _get_fragmentation_bit(self, value_frame):
        """
        Return fragmention_bit
        """
        bit_mask_framention = 0x800
        fragmention_bit = value_frame & bit_mask_framention
        status = 'False'
        if fragmention_bit:
            status = 'True'
        else:
            status = 'False'
        return status

    def _get_type(self, value_frame):
        """
        Return format type
        """
        bit_mask_format_type = 0xF000
        format_type = value_frame & bit_mask_format_type
        value_type = 0
        if format_type == 40960:
            value_type = 3
        else:
            value_type = format_type
        return value_type

    def _add_frame_format(self):
        """
        Take first and second bytes and record to structure - it is
        field "frame format" in Message.
        Call methods, witch calculate length fields "frame format" and
        add the structure FieldFrameFormat in the structure Message.
        """
        if self.position == 1:
            f_f = self.bytes[1:3:].encode('hex')
            Message.frame_format = f_f
            self.position += 1
            value_frame = int(Message.frame_format, 16)
            frame_len = self._get_len(value_frame)
            fragmention_bit = self._get_fragmentation_bit(value_frame)
            format_type = self._get_type(value_frame)
            FieldFrameFormat.frame_len = frame_len
            FieldFrameFormat.fragmention_bit = fragmention_bit
            FieldFrameFormat.format_type = format_type
            Message.frame_format = FieldFrameFormat

    def _add_address(self):
        """
        Take third and next bytes and record to structure - these are
        fields "dest address" or "scr address" in structure.
        They may be 1, 2 or 4 bytes
        """
        value_end = 0x1
        bytes_address = ''
        position_dest_addr = 3
        position_src_addr = 0
        if self.position == 2:
            for _ in range(0, 4):
                bytes_address = bytes_address + self.bytes[position_dest_addr]
                number_address = int(bytes_address.encode('hex'), 16)
                if number_address & value_end:
                    Message.dest_addr = bytes_address.encode('hex')
                    self.position += 1
                    position_src_addr = position_dest_addr + 1
                    break
                else:
                    position_dest_addr += 1
        bytes_address = ''
        if self.position == 3:
            for _ in range(0, 4):
                bytes_address = bytes_address + self.bytes[position_src_addr]
                number_address = int(bytes_address.encode('hex'), 16)
                if number_address & value_end:
                    Message.scr_addr = bytes_address.encode('hex')
                    self.position += 1
                    self.position_controll = position_src_addr + 1
                    break
                else:
                    position_src_addr += 1

    def _get_lsb(self, value_controll):
        """Return  LSB """
        bit_mask_lsb = 0x1
        lsb = value_controll & bit_mask_lsb
        return lsb

    def _get_poll_fin(self, value_conroll):
        """Return value poll or final the bits"""
        bit_mask_poll_final = 0x10
        poll_final = value_conroll & bit_mask_poll_final
        value = 0
        if poll_final == 16:
            value = 1
        else:
            value = poll_final
        return value

    def _get_recive(self, value_conroll):
        """Return receive sequence number"""
        bit_mask_recive = 0xe0
        recive = value_conroll & bit_mask_recive
        return recive

    def _get_send(self, value_conroll):
        """Return send sequence number"""
        bit_mask_send = 0xe
        send = value_conroll & bit_mask_send
        return send

    def _define_type_field_controll(self, send, recive, lsb):
        """ Define type the command or response"""
        if lsb == 0x0:
            FieldControll.command_response = 'I'
        elif recive == 0x80 and send == 0x2:
            FieldControll.command_response = 'SNRM'
        elif recive == 0x40 and send == 0x2:
            FieldControll.command_response = 'DISC'
        elif recive == 0x60 and send == 0x2:
            FieldControll.send = 'UA'
        elif recive == 0x00 and send == 0xe:
            FieldControll.send = 'DM'
        elif recive == 0x80 and send == 0x6:
            FieldControll.send = 'FRMR'
        elif recive == 0x0 and send == 0x2:
            FieldControll.send = 'UI'
        elif send == 0x4:
            FieldControll.send = 'RNR'
        elif send == 0x0:
            FieldControll.send = 'RR'

    def _add_controll(self):
        """
        Calculate field values "control" and they add in the structure
        'FieldControll'. Structure FieldControll records in
        the structure 'Message'.
        The field contain 1 byte
        """
        if self.position == 4:
            controll = self.bytes[self.position_controll]
            Message.control = controll.encode('hex')
            self.position += 1
            self.position_hcs = self.position_controll + 1
            value_controll = int(Message.control, 16)
            lsb = self._get_lsb(value_controll)
            poll_final = self._get_poll_fin(value_controll)
            send = self._get_send(value_controll)
            recive = self._get_recive(value_controll)
            self._define_type_field_controll(send, recive, lsb)
            FieldControll.send = send
            FieldControll.recive = recive
            FieldControll.lsb = lsb
            FieldControll.poll_finall = poll_final
            Message.control = FieldControll

    def _check_hcs(self, hcs):
        """
        Check 'header check sequence' with real the number bytes: frame format,
        dest address, scr address, control, hcs
        """
        try:
            start_flag = 1
            hcs_bytes = 2
            if (self.position_hcs + hcs_bytes - start_flag) == hcs:
                return True
            else:
                raise CheckSummError()
        except CheckSummError as exc:
            print ("Value field 'hcs' is not correct", exc)

    def _add_hcs(self):
        """
        Take next bytes after "field control" and record to structure -
        these are fields "hcs" in structure. It is the field - header
        check sequence. The field contain 2 bytes
        """
        if self.position == 5:
            num_bytes_hcs = 2
            hcs = self.bytes[self.position_hcs]
            hcs = hcs.encode('hex')
            hcs = int(hcs, 16)
            status = self._check_hcs(hcs)
            if status is True:
                Message.hcs = hcs
            self.position += 1
            self.position_info = self.position_hcs + num_bytes_hcs

    def _add_information(self):
        """
        Calculate length the field "information".
        The field may be any sequence of bytes.
        """
        if self.position == 6:
            cons = 3
            bytes_info = ''
            len_info = FieldFrameFormat.frame_len - self.position_hcs - cons
            start_pos_info = self.position_info
            for _ in range(0, len_info):
                bytes_info = bytes_info + self.bytes[start_pos_info]
                start_pos_info += 1
            Message.information = bytes_info.encode('hex')
            self.position_fcs = start_pos_info
            self.position += 1

    def _add_fcs(self):
        """
        Add 'frame check sequence' in the structure.
        The field have length 2 bytes.
        """
        if self.position == 7:
            fcs_bytes = 2
            fcs = self.bytes[self.position_fcs: self.position_fcs + fcs_bytes:]
            Message.fcs = fcs.encode('hex')
            Message.fcs = int(Message.fcs, 16)
            self.position += 1
            self.position_flag_end = self.position_fcs + fcs_bytes

    def print_message(self):
        print self.message

    # def print_message(self):
    #     """Print all fields decoded and parse string"""
    #     for name in Message._fields:
    #         if name == 'frame_format':
    #             self.print_field_frame_format()
    #         elif name == 'control':
    #             self.print_controll_field()
    #         else:
    #             print name, ':', getattr(Message, name)

    # def print_field_frame_format(self):
    #     """Print the structure 'FieldFrameFormat'"""
    #     print 'frame format:'
    #     for name in FieldFrameFormat._fields:
    #         print '    ', name, ':', getattr(FieldFrameFormat, name)

    # def print_controll_field(self):
    #     """Print the structure 'FieldControll'"""
    #     print 'control:'
    #     for name in FieldControll._fields:
    #         print '    ', name, ':', getattr(FieldControll, name)

    def pars_msg(self, data):
        """Parsing the string and add the values in the structure"""
        self.transformation_to_bytes(data)
        self._add_flag()
        self._add_frame_format()
        self._add_address()
        self._add_address()
        self._add_controll()
        self._add_hcs()
        self._add_information()
        self._add_fcs()
        self._add_flag()
        self.print_message()


def main(data):
    """Create an instance and call main method, witch parsing the string"""
    pars = Parser()
    parced_msg = pars.pars_msg(data)
    print parced_msg


if __name__ == '__main__':
    main(
        "7ea0586103300751e6e700614aa109060760857405080101a2030201"
        "00a305a10302010e88020780890760857405080202aa1280106162636"
        "465666768696a6b6c6d6e6f70be10040e0800065f1f040000181d0164000718d07e"
    )
