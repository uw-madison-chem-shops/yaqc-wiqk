import yaqc
import qtypes
from yaqc_qtpy import QClient


class Valve:
    def __init__(self, port, index):
        self.port = port
        self.qclient = QClient(host="127.0.0.1", port=port)
        self.enum = qtypes.Enum(str(index), value={"allowed": ["A", "B"]})
        self.qclient.properties.position_identifier.updated.connect(
            self._on_position_identifier_updated
        )
        self.enum.edited.connect(self._on_enum_edited)

    def _on_position_identifier_updated(self, result):
        self.enum.set_value(result)

    def _on_enum_edited(self, result):
        self.qclient.set_identifier(result["value"])
