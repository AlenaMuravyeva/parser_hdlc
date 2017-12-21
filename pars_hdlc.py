
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
    """Total structure message"""
    def __str__(self):
        """Override magic method __str__, for print """
        fmt = [
            'Flag: {}\n'.format(self.flag),
            'Frame format: {}\n'.format(self.frame_format),
            'Destination address: {}\n'.format(self.dest_addr),
            'Source address: {}\n'.format(self.scr_addr),
            'Control: {}\n'.format(self.control),
            'Header check sequence:{}\n'.format(self.hcs),
            'Information: {}\n'.format(self.information),
            'Frame check sequence:{}\n'.format(self.fcs),
            'Flag:{}\n'.format(self.flag_end),
        ]
        return ''.join(fmt)


class FrameFormat(
        collections.namedtuple(
            'FrameFormat',
            [
                'frame_len',
                'fragmention_bit',
                'format_type'
            ]
        )
):
    """Detail structure field "frame_format" in structure 'Message'"""
    def __str__(self):
        """Override magic method __str__, for print """
        fmt = [
            '\n\tFrame length:{}'.format(self.frame_len),
            '\n\tSegmentation bit:{}'.format(self.fragmention_bit),
            '\n\tFormat type:{}'.format(self.format_type)
        ]
        return ''.join(fmt)


class Control(
        collections.namedtuple(
            "Control", [
                'lsb',
                'command_response',
                'recive',
                'send',
                'poll_finall'
            ]
        )
):
    """Detail structure field "control" in structure 'Message'"""
    def __str__(self):
        """Override magic method __str__, for print """
        fmt = [
            '\n\tLSB:{}'.format(self.lsb),
            '\n\tCommand/Response:{}'.format(self.command_response),
            '\n\tReceive:{}'.format(self.recive),
            '\n\tSend:{}'.format(self.send),
            '\n\tPoll/Final:{}'.format(self.poll_finall)
        ]
        return ''.join(fmt)


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
        self.position_controll = 0
        self.position_hcs = 0
        self.position_info = 0
        self.position_fcs = 0
        self.position_flag_end = 0
        self.value_frame = 0
        self.position_src_addr = 0
        self.position_dest_addr = 3

    def transformation_to_bytes(self, data):
        """Converts to byte string."""
        self.data = data
        file_bytes = StringIO.StringIO(self.data.decode('hex'))
        for byte in file_bytes:
            str_bytes = byte
            return str_bytes

    def _add_flag(self, srt_bytes):
        """
        Extract the flags from Message
         """
        flag = ''
        if self.position == 0 and srt_bytes[0] == '7e'.decode('hex'):
            flag = srt_bytes[0].encode('hex')
            self.position += 1
        if self.position == 8:
            flag = srt_bytes[self.position_flag_end]
            flag = flag.encode('hex')
        return flag
        # flag = srt_bytes.read(1)
        # if flag != '7e'.decode('hex'):
        #     raise ValueError("wrong frame guard")
        # return flag

    def _get_len(self):
        """
        Return frame length
        """
        bit_mask_lenght = 0x7FF
        field_frame_format_len = self.value_frame & bit_mask_lenght
        return field_frame_format_len

    def _get_fragmentation_bit(self):
        """
        Return fragmention_bit
        """
        bit_mask_framention = 0x800
        fragmention_bit = self.value_frame & bit_mask_framention
        status = 'False'
        if fragmention_bit:
            status = 'True'
        else:
            status = 'False'
        return status

    def _get_type(self):
        """
        Return format type
        """
        bit_mask_format_type = 0xF000
        format_type = self.value_frame & bit_mask_format_type
        value_type = 0
        if format_type == 40960:
            value_type = 3
        else:
            value_type = format_type
        return value_type

    def _add_frame_format(self, srt_bytes):
        """
        Take first and second bytes and record to structure - it is
        field "frame format" in Message.
        Call methods, witch calculate length fields "frame format" and
        add the structure FieldFrameFormat in the structure Message.
        """
        if self.position == 1:
            f_f = srt_bytes[1:3:].encode('hex')
            self.position += 1
            self.value_frame = int(f_f, 16)
            frame_len = self._get_len()
            fragmention_bit = self._get_fragmentation_bit()
            format_type = self._get_type()
            frame_format = {
                'frame_len': frame_len,
                'fragmention_bit': fragmention_bit,
                'format_type': format_type,
            }
            return frame_format

    def _add_dest_address(self, srt_bytes):
        """
        Take third and next bytes and record to structure - these are
        fields "dest address" in structure.
        They may be 1, 2 or 4 bytes
        """
        value_end = 0x1
        bytes_addrr = ''
        if self.position == 2:
            for _ in range(0, 4):
                bytes_addrr = bytes_addrr + srt_bytes[self.position_dest_addr]
                number_address = int(bytes_addrr.encode('hex'), 16)
                if number_address & value_end:
                    bytes_addrr = bytes_addrr.encode('hex')
                    self.position += 1
                    self.position_src_addr = self.position_dest_addr + 1
                    break
                else:
                    self.position_dest_addr += 1
        return bytes_addrr

    def _add_scr_address(self, srt_bytes):
        """
        """
        value_end = 0x1
        bytes_addrr = ''
        if self.position == 3:
            for _ in range(0, 4):
                bytes_addrr = bytes_addrr + srt_bytes[self.position_src_addr]
                number_address = int(bytes_addrr.encode('hex'), 16)
                if number_address & value_end:
                    bytes_addrr = bytes_addrr.encode('hex')
                    self.position += 1
                    self.position_controll = self.position_src_addr + 1
                    break
                else:
                    self.position_src_addr += 1
        return bytes_addrr

    def _get_lsb(self):
        """Return  LSB """
        bit_mask_lsb = 0x1
        lsb = self.value_controll & bit_mask_lsb
        return lsb

    def _get_poll_fin(self):
        """Return value poll or final the bits"""
        bit_mask_poll_final = 0x10
        poll_final = self.value_controll & bit_mask_poll_final
        value = 0
        if poll_final == 16:
            value = 1
        else:
            value = poll_final
        return value

    def _get_recive(self):
        """Return receive sequence number"""
        bit_mask_recive = 0xe0
        recive = self.value_controll & bit_mask_recive
        return recive

    def _get_send(self):
        """Return send sequence number"""
        bit_mask_send = 0xe
        send = self.value_controll & bit_mask_send
        return send

    def _define_type_field_control(self, send, recive, lsb):
        """ Define type the command or response"""
        type_control = ''
        if lsb == 0x0:
            type_control = 'I'
        elif recive == 0x80 and send == 0x2:
            type_control = 'SNRM'
        elif recive == 0x40 and send == 0x2:
            type_control = 'DISC'
        elif recive == 0x60 and send == 0x2:
            type_control = 'UA'
        elif recive == 0x00 and send == 0xe:
            type_control = 'DM'
        elif recive == 0x80 and send == 0x6:
            type_control = 'FRMR'
        elif recive == 0x0 and send == 0x2:
            type_control = 'UI'
        elif send == 0x4:
            type_control = 'RNR'
        elif send == 0x0:
            type_control = 'RR'

        return type_control

    def _add_controll(self, srt_bytes):
        """
        Calculate field values "control" and they add in the structure
        'FieldControll'. Structure FieldControll records in
        the structure 'Message'.
        The field contain 1 byte
        """
        if self.position == 4:
            control = srt_bytes[self.position_controll]
            control = control.encode('hex')
            self.position += 1
            self.position_hcs = self.position_controll + 1
            self.value_controll = int(control, 16)
            lsb = self._get_lsb()
            poll_final = self._get_poll_fin()
            send = self._get_send()
            recive = self._get_recive()
            type_control = self._define_type_field_control(send, recive, lsb)
            control = {
                'command_response': type_control,
                'send': send,
                'recive': recive,
                'lsb': lsb,
                'poll_finall': poll_final,
            }
            return control

    def _check_hcs(self, hcs):
        """
        Check 'header check sequence' with real the number bytes: frame format,
        dest address, scr address, control, hcs
        """
        try:
            start_flag = 1
            hcs_bytes = 2
            print (self.position_hcs + hcs_bytes - start_flag)
            print hcs
            if (self.position_hcs + hcs_bytes - start_flag) == hcs:
                return True
            else:
                raise CheckSummError()
        except CheckSummError as exc:
            print ("Value field 'hcs' is not correct", exc)

    def _add_hcs(self, srt_bytes):
        """
        Take next bytes after "field control" and record to structure -
        these are fields "hcs" in structure. It is the field - header
        check sequence. The field contain 2 bytes
        """
        if self.position == 5:
            num_bytes_hcs = 2
            hcs = srt_bytes[self.position_hcs]
            hcs = hcs.encode('hex')
            hcs = int(hcs, 16)
            # status = self._check_hcs(hcs)
            # if status is True:
            self.position += 1
            self.position_info = self.position_hcs + num_bytes_hcs
            return hcs

    def _add_information(self, srt_bytes, frame_format):
        """
        Calculate length the field "information".
        The field may be any sequence of bytes.
        """
        if self.position == 6:
            cons = 3
            bytes_info = ''
            frame_len = frame_format['frame_len']
            len_info = frame_len - cons
            len_info = len_info - self.position_hcs
            start_pos_info = self.position_info
            for _ in range(0, len_info):
                bytes_info = bytes_info + srt_bytes[start_pos_info]
                start_pos_info += 1
            information = bytes_info.encode('hex')
            self.position_fcs = start_pos_info
            self.position += 1
            return information

    def _add_fcs(self, srt_bytes):
        """
        Add 'frame check sequence' in the structure.
        The field have length 2 bytes.
        """
        if self.position == 7:
            fcs_bytes = 2
            fcs = srt_bytes[self.position_fcs: self.position_fcs + fcs_bytes:]
            fcs = fcs.encode('hex')
            fcs = int(fcs, 16)
            self.position += 1
            self.position_flag_end = self.position_fcs + fcs_bytes
            return fcs

    def _construct_data_object(self, data):
        """Create instances Message, FrameFormat, Control"""
        message = Message(
            flag=data['flag'],
            frame_format=FrameFormat(
                frame_len=data['frame_format']['frame_len'],
                fragmention_bit=data['frame_format']['fragmention_bit'],
                format_type=data['frame_format']['format_type'],
            ),
            dest_addr=data['dest_address'],
            scr_addr=data['scr_address'],
            control=Control(
                lsb=data['control']['lsb'],
                command_response=data['control']['command_response'],
                recive=data['control']['recive'],
                send=data['control']['send'],
                poll_finall=data['control']['poll_finall'],
            ),
            hcs=data['hcs'],
            information=data['information'],
            fcs=data['fcs'],
            flag_end=data['flag_end'],
        )
        return message

    def get_payload(self, data):
        """
        Parsing the string and add the values in the _dict, return
        instance 'Message'
        """
        srt_bytes = self.transformation_to_bytes(data)

        flag = self._add_flag(srt_bytes)
        frame_format = self._add_frame_format(srt_bytes)
        dest_address = self._add_dest_address(srt_bytes)
        scr_address = self._add_scr_address(srt_bytes)
        control = self._add_controll(srt_bytes)
        hcs = self._add_hcs(srt_bytes)
        information = self._add_information(srt_bytes, frame_format)
        fcs = self._add_fcs(srt_bytes)
        flag_end = self._add_flag(srt_bytes)

        data = {
            'flag': flag,
            'frame_format': frame_format,
            'dest_address': dest_address,
            'scr_address': scr_address,
            'control': control,
            'hcs': hcs,
            'information': information,
            'fcs': fcs,
            'flag_end': flag_end,
        }
        msg = self._construct_data_object(data)
        return msg


def main(data):
    """
    Create an instance and call main method, witch parsing the string
    Print disassembled data
    """
    pars = Parser()
    parced_msg = pars.get_payload(data)
    print parced_msg


if __name__ == '__main__':
    main(
        "7ea011610330d3bee6e700c70181010052ab7e"
    )
