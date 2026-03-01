from typing import List, Optional

class Cell:
    _counter = 0
    def __init__(self):
        Cell._counter += 1
        self.id      = Cell._counter
        self.content = ""
        self.result: Optional[dict] = None
        self.running = False
        self._suggestion_panel = None
        self._textarea         = None
        self._output_area      = None
        self._spinner_btn      = None

cells: List[Cell] = [Cell()]
cells_container   = None
files_panel       = None
voice_btn         = None
voice_status      = None
