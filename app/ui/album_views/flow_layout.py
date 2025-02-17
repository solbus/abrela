from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtWidgets import QLayout

class FlowLayout(QLayout):
    """
    A custom flow layout that arranges widgets in a flowing manner, wrapping them as needed.
    This centers each line of items horizontally.
    """
    def __init__(self, parent=None, margin=0, hSpacing=10, vSpacing=10):
        super().__init__(parent)
        self.itemList = []
        self.m_hSpace = hSpacing
        self.m_vSpace = vSpacing
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def isEmpty(self):
        return len(self.itemList) == 0

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        margins = self.contentsMargins()
        effectiveRect = QRect(rect.x() + margins.left(), rect.y() + margins.top(),
                            rect.width() - (margins.left() + margins.right()),
                            rect.height() - (margins.top() + margins.bottom()))

        y = effectiveRect.y()
        spaceX = self.m_hSpace
        spaceY = self.m_vSpace
        lineHeight = 0
        lineItems = []
        currentX = effectiveRect.x()

        for item in self.itemList:
            hint = item.sizeHint()
            w = hint.width()
            h = hint.height()

            # If adding this item would exceed the width, we lay out the current line first
            if lineItems and (currentX + w) > effectiveRect.right():
                # Lay out the current line centered
                y = self.layoutLine(effectiveRect, lineItems, lineHeight, testOnly, y, spaceX)

                # Start a new line
                lineItems = []
                lineHeight = 0
                currentX = effectiveRect.x()

            lineItems.append((item, w, h))
            currentX += w + spaceX
            lineHeight = max(lineHeight, h)

        # Layout the last line if any items remain
        if lineItems:
            y = self.layoutLine(effectiveRect, lineItems, lineHeight, testOnly, y, spaceX)

        return y - rect.y() + margins.bottom()

    def layoutLine(self, effectiveRect, lineItems, lineHeight, testOnly, y, spaceX):
        # Calculate total line width
        totalWidth = 0
        for (item, w, h) in lineItems:
            totalWidth += w
        totalWidth += spaceX * (len(lineItems)-1) if len(lineItems) > 1 else 0

        # Center the line
        extraSpace = effectiveRect.width() - totalWidth
        startX = effectiveRect.x() + extraSpace//2

        # Set item geometry if not testOnly
        if not testOnly:
            x = startX
            for (item, w, h) in lineItems:
                item.setGeometry(QRect(x, y, w, h))
                x += w + spaceX

        # Move down for next line
        return y + lineHeight + self.m_vSpace
