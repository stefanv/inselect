from PySide import QtGui, QtCore

import inselect.settings
from inselect.gui.annotator import AnnotateDialog


class SegmentListWidget(QtGui.QListWidget):
    def __init__(self, segment_scene, parent=None):
        # Constructors
        super(SegmentListWidget, self).__init__(parent)
        # Set up members
        self.enable = True
        self.parent = parent
        self.segment_scene = segment_scene
        # Setup UI
        self.setIconSize(QtCore.QSize(100, 100))
        self.setViewMode(QtGui.QListView.IconMode)
        self.setDragEnabled(False)
        self.setResizeMode(QtGui.QListView.Adjust)
        self.setMovement(QtGui.QListView.Static)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.setMinimumWidth(100)
        # Watch for new/removed segments
        self.segment_scene.watch('after-segment-add', self._after_segment_add)
        self.segment_scene.watch('before-segment-remove',
                                 self._before_segment_remove)

    def selectionChanged(self, selected_items, deselected_items):
        for i in range(self.count()):
            item = self.item(i)
            selected = item.isSelected()
            segment = self.segment_scene.get_associated_segment(item)
            box = self.segment_scene.get_associated_object('boxResizable',
                                                           segment)
            box.setSelected(selected)
        QtGui.QListWidget.selectionChanged(self, selected_items,
                                           deselected_items)

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Return,
                           ord('Z')]:
            self.parent.view.keyPressEvent(event)
        QtGui.QListWidget.keyPressEvent(self, event)

    def on_item_double_clicked(self, item):
        segment = self.segment_scene.get_associated_segment(item)
        dialog = AnnotateDialog(self.segment_scene, segment,
                                parent=self.parent)
        dialog.exec_()

    def _after_segment_add(self, segment):
        """Called when a new segment is added to the segment scene

        Parameters
        ----------
        segment : Segment
        """
        list_item = QtGui.QListWidgetItem()
        index = self.segment_scene.get_segment_index(segment)
        self.insertItem(index, list_item)
        self.segment_scene.associate_object('listWidgetItem',
                                            list_item, segment)
        # Watch the segment to update the icon/label.
        segment.watch('after-corners-update', self._update_segment)
        segment.watch('after-fields-update', self._update_segment)
        # Trigger an update to set icon/text
        self._update_segment(segment)

    def _update_segment(self, segment):
        """Called when the segment is updated

        Parameters
        ----------
        segment : Segment
        """
        # TODO: Re-order the list.
        icon = self.segment_scene.get_segment_icon(segment)
        default_label = inselect.settings.get('label_field')
        fields = segment.fields()
        text = ""
        if default_label in fields:
            text = fields[default_label]
        list_item = self.segment_scene.get_associated_object('listWidgetItem',
                                                             segment)
        list_item.setIcon(icon)
        list_item.setText(text)

    def _before_segment_remove(self, segment):
        """Called when a segment is removed from the scene

        Parameters
        ----------
        segment : Segment
        """
        list_item = self.segment_scene.get_associated_object('listWidgetItem',
                                                             segment)
        self.takeItem(self.row(list_item))
