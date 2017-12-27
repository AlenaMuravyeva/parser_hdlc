
"""HDLC parser."""
import collections
import StringIO
import check_summ


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
            'Header check sequence:{:}\n'.format(self.hcs),
            'Information: {}\n'.format(self.information),
            'Frame check sequence:{:}\n'.format(self.fcs),
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
    """Detail structure field "frame_format" in the class 'Message'"""
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
    """Detail structure field "control" in the class 'Message'"""
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


class LenghtError(Exception):
    """
    Exception raised, if lenght is not correct
    """
    pass


class Parser(object):
    """ HDLC parser"""
    def __init__(self):
        """Initialization fields"""
        self.counter_readed_bytes = 0
        self.raw_frame = None

    def transformation_to_bytes(self, data):
        """Converts to byte string and assign value raw_frame"""
        file_bytes = StringIO.StringIO(data.decode('hex'))
        self.raw_frame = data
        return file_bytes

    def _get_flag(self, srt_bytes):
        """
        Return the flags from Message
         """
        flag = srt_bytes.read(1)
        if flag != '7e'.decode('hex'):
            raise ValueError("wrong frame guard")
        self.counter_readed_bytes += 1
        flag = flag.encode('hex')
        return flag

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

    def _get_frame_format(self, srt_bytes):
        """
        Return fields 'frame format'.
        Call methods, witch get length fields:"frame format", "segmentation
        bit", "format type".
        """
        frame_format = srt_bytes.read(2)
        value_frame_format = frame_format.encode('hex')
        value_frame = int(value_frame_format, 16)
        frame_len = self._get_len(value_frame)
        fragmention_bit = self._get_fragmentation_bit(value_frame)
        format_type = self._get_type(value_frame)
        frame_format = {
            'frame_len': frame_len,
            'fragmention_bit': fragmention_bit,
            'format_type': format_type,
        }
        self.counter_readed_bytes += 2
        return frame_format

    def _get_address(self, srt_bytes):
        """
        Return value "destination address"  or "source address".
        They may be 1, 2 or 4 bytes.
        """
        value_end = 0x1
        bytes_addrr = ''
        for _ in range(0, 4):
            bytes_addrr = bytes_addrr + srt_bytes.read(1)
            number_address = int(bytes_addrr.encode('hex'), 16)
            self.counter_readed_bytes += 1
            if number_address & value_end:
                bytes_addrr = bytes_addrr.encode('hex')
                break
            else:
                continue
        return bytes_addrr

    def _get_lsb(self, value_controll):
        """Return  LSB """
        bit_mask_lsb = 0x1
        lsb = value_controll & bit_mask_lsb
        return lsb

    def _get_poll_fin(self, value_controll):
        """Return value poll or final the bits"""
        bit_mask_poll_final = 0x10
        poll_final = value_controll & bit_mask_poll_final
        value = 0
        if poll_final == 16:
            value = 1
        else:
            value = poll_final
        return value

    def _get_recive(self, value_controll):
        """Return receive sequence number"""
        bit_mask_recive = 0xe0
        recive = value_controll & bit_mask_recive
        return recive

    def _get_send(self, value_controll):
        """Return send sequence number"""
        bit_mask_send = 0xe
        send = value_controll & bit_mask_send
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

    def _get_control(self, srt_bytes):
        """
        Return field values"control": "lsb","poll_final", "send", "receive",
        "type_conroll". The field contain 1 byte
        """
        control = srt_bytes.read(1)
        control = control.encode('hex')
        value_controll = int(control, 16)
        lsb = self._get_lsb(value_controll)
        poll_final = self._get_poll_fin(value_controll)
        send = self._get_send(value_controll)
        recive = self._get_recive(value_controll)
        type_control = self._define_type_field_control(send, recive, lsb)
        control = {
            'command_response': type_control,
            'send': send,
            'recive': recive,
            'lsb': lsb,
            'poll_finall': poll_final,
        }
        self.counter_readed_bytes += 1
        return control

    def _validate_checksum(self, expected, value, checksum_type):
        """Check header check sequence."""
        calculated_checksum = check_summ.checksum(value)
        if expected != calculated_checksum:
            raise CheckSummError(
                "{} checksum validation failed. Expected {:}, got {:}".format
                (
                    checksum_type, expected, calculated_checksum
                )
            )

    def _get_hcs(self, srt_bytes):
        """Return value header check sequence. The field contain 2 bytes"""
        hcs = int(srt_bytes.read(2).encode('hex'), 16)
        hcs = (hcs >> 8 | hcs << 8) & 0xFFFF
        value = self.raw_frame[2:(self.counter_readed_bytes * 2)]
        value = value.decode('hex')
        self._validate_checksum(hcs, value, "HCS")
        self.counter_readed_bytes += 2
        return hcs

    def _get_information(self, srt_bytes, frame_format):
        """
        Calculate length the field "information".
        The field may be any sequence of bytes.
        """
        first_flag = 1
        frame_len = frame_format['frame_len']
        len_info = frame_len - first_flag - self.counter_readed_bytes
        information = srt_bytes.read(len_info)
        information = information.encode('hex')
        self.counter_readed_bytes += len_info
        return information

    def _get_fcs(self, srt_bytes, frame_format):
        """Return frame check sequence.The field have length 2 bytes."""
        fcs = int(srt_bytes.read(2).encode('hex'), 16)
        fcs = (fcs >> 8 | fcs << 8) & 0xFFFF
        value = self.raw_frame[2:-6]
        self._validate_checksum(fcs, value.decode('hex'), "FCS")
        self.counter_readed_bytes += 2
        self._validation_lenght(frame_format)
        return fcs

    def _validation_lenght(self, frame_format):
        """Validation frame lenght"""
        expected = frame_format['frame_len']
        frame_len = self.counter_readed_bytes - 1
        if expected != frame_len:
            raise LenghtError(
                "lenght validation failed. Expected {:}, got {:}".format(
                    expected, frame_len
                )
            )

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
        information = None
        fcs = None
        flag_end = None
        srt_bytes = self.transformation_to_bytes(data)
        flag = self._get_flag(srt_bytes)
        frame_format = self._get_frame_format(srt_bytes)
        dest_address = self._get_address(srt_bytes)
        scr_address = self._get_address(srt_bytes)
        control = self._get_control(srt_bytes)
        hcs = self._get_hcs(srt_bytes)
        if frame_format['frame_len'] == self.counter_readed_bytes - 1:
            flag_end = self._get_flag(srt_bytes)
        else:
            information = self._get_information(srt_bytes, frame_format)
            fcs = self._get_fcs(srt_bytes, frame_format)
            flag_end = self._get_flag(srt_bytes)

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
        "7ea0200361931b9f8180140502080006020800070400000007080400000007b3c67e"
    )
