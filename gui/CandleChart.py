import math
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart


# ------------------------------------------------------------------------------------
# Candle Chart
# ------------------------------------------------------------------------------------

class CandleChart(QtChart.QChart):
    """Actual Candle chart display."""
    ax = None
    ay = None
    minTicks = 5
    maxTicks = 10
    # time frames in minutes: 1m, 5m, 10m, 15m, 30m, 1h, 2h, 3h, 6h, 12h, 1d, 3d, 1w
    time_frames = [1, 5, 10, 15, 30, 60, 120, 180, 360, 720, 1440, 4320, 10080]

    def __init__(self):
        super(CandleChart, self).__init__()

        # set margins, colors and font
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        self.setBackgroundRoundness(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setMargins(QtCore.QMargins(0, 0, 0, 0))
        self.legend().hide()
        chartFont = QtGui.QFont(self.font())
        chartFont.setPixelSize(9)
        self.setFont(chartFont)

        self.candlestickSeries = QtChart.QCandlestickSeries()
        self.candlestickSeries.setIncreasingColor(QtCore.Qt.black)
        self.candlestickSeries.setDecreasingColor(QtCore.Qt.red)
        self.addSeries(self.candlestickSeries)

        # add hover line and price tag
        self.setAcceptHoverEvents(True)
        self.hoverLinePriceTag = QtWidgets.QGraphicsSimpleTextItem(self)
        self.hoverLinePriceTag.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.hoverLinePriceTag.setOpacity(1.0)
        self.hoverLine = QtChart.QLineSeries()
        hoverPen = QtGui.QPen(QtCore.Qt.DashLine)
        hoverPen.setColor(QtCore.Qt.white)
        hoverPen.setWidthF(0.5)
        hoverPen.setDashPattern([5, 10])
        self.hoverLine.setPen(hoverPen)
        self.hoverLineAxisX = QtChart.QValueAxis()
        self.hoverLineAxisX.hide()
        self.hoverLineAxisX.setRange(0, 1)
        self.addSeries(self.hoverLine)
        self.addAxis(self.hoverLineAxisX, QtCore.Qt.AlignBottom)
        self.hoverLine.attachAxis(self.hoverLineAxisX)


    def updateCandleChart(self, data, N):
        """Update candle chart display.
        :param data:  numpy array representing candles
        :param N:     number of candles in the array
        """
        if data is None or data == []:
            return

        timestamps = data[0, -N:].astype(int).tolist()
        open       = data[1, -N:].tolist()
        high       = data[2, -N:].tolist()
        low        = data[3, -N:].tolist()
        close      = data[4, -N:].tolist()

        # remove candlestick data
        if self.candlestickSeries.count() > 0:
            self.candlestickSeries.remove(self.candlestickSeries.sets())

        # add new candlestick data
        for i, ts in enumerate(timestamps):
            candle_set = QtChart.QCandlestickSet(open[i], high[i], low[i], close[i], timestamp=ts)
            self.setCandleColors(candle_set)
            self.candlestickSeries.append(candle_set)

        # set candlestick time axes (hidden)
        axisXtime = QtChart.QBarCategoryAxis()
        axisXtime.setCategories([str(int(x / 1000)) for x in timestamps])
        axisXtime.setGridLineVisible(False)
        axisXtime.hide()

        self.ax = QtChart.QValueAxis()
        self.ax.setRange(0, len(axisXtime))
        self.ax.setGridLineVisible(False)
        self.ax.hide()

        # set pen for lines and grid lines
        line_pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5)
        grid_line_pen = QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5)

        # set visible time axes with selected time ticks
        axisXticks = QtChart.QCategoryAxis()
        axisXticks.setLabelsPosition(QtChart.QCategoryAxis.AxisLabelsPositionOnValue)
        for ts, index in self.extractNiceCategories(timestamps):
            axisXticks.append(ts, index)
        axisXticks.setGridLineVisible(True)
        axisXticks.setGridLinePen(grid_line_pen)
        axisXticks.setLinePen(line_pen)
        axisXticks.setStartValue(-1)

        # set y axes (prices)
        max_val = max(high)
        min_val = min(low)
        self.ay = QtChart.QValueAxis()
        self.ay.setGridLinePen(grid_line_pen)
        self.ay.setLinePen(line_pen)
        self.ay.setMax(max_val)
        self.ay.setMin(min_val)
        self.ay.applyNiceNumbers()

        # set y axes font
        font = self.ay.labelsFont()
        font.setPointSize(8)
        self.ay.setLabelsFont(font)

        # remove old axes
        for axis in self.candlestickSeries.attachedAxes():
            self.candlestickSeries.detachAxis(axis)
            self.removeAxis(axis)

        # add updated axes
        self.addAxis(axisXtime, QtCore.Qt.AlignTop)
        self.addAxis(axisXticks, QtCore.Qt.AlignBottom)
        self.addAxis(self.ax, QtCore.Qt.AlignBottom)
        self.addAxis(self.ay, QtCore.Qt.AlignRight)

        # attach updated axes to data series
        self.candlestickSeries.attachAxis(axisXtime)
        self.candlestickSeries.attachAxis(axisXticks)
        self.candlestickSeries.attachAxis(self.ay)

        # update hover line x axes
        for axis in self.hoverLine.attachedAxes():
            self.hoverLine.detachAxis(axis)
        self.hoverLine.attachAxis(self.ay)


    def extractNiceCategories(self, timestapms):
        """Chooses appropriate ticks for visible time axes.
        :param timestapms:   a list of timestamps for currently visible candles
        :returns list of tuples [(time_string, index), ... ]
        Tries to select and to show approximately between 4 and 12 ticks on the time axes.
        If possible, it will adjust to local time (works only with small candle intervals).
        As long as the candle interval is larger than the local timezone offset from UTC
        the chart will use UTC time. This is because exchanges use UTC timestamps.
        """
        # get the interval between two candles in minutes
        candle_interval = timestapms[1] - timestapms[0]

        # find the time frame with which we get between 4 and 12 ticks
        for frame in self.time_frames:
            if 4 <= len(timestapms) * candle_interval / (60000 * frame) <= 12:
                break

        # get the local timezone offset from UTC in milliseconds and select the time spec
        local_offset = 1000 * QtCore.QDateTime.currentDateTime().offsetFromUtc()
        time_spec = QtCore.Qt.LocalTime
        if candle_interval > local_offset:
            local_offset = 0
            time_spec = QtCore.Qt.UTC

        # select the timestamps and their indexes using the chosen time frame
        # return the timestamps as formatted strings
        num_ticks = 0
        selected_timestamps = []
        for index, val in enumerate(timestapms):
            time_str = QtCore.QDateTime.fromMSecsSinceEpoch(val, time_spec).toString('yyyy:MMM:dd:HH:mm')

            if (val + local_offset) % (60000 * frame) == 0:
                if time_str.endswith('Jan:01:00:00'):
                    time_str = QtCore.QDateTime.fromMSecsSinceEpoch(val, time_spec).toString('yyyy')
                elif time_str.endswith('01:00:00'):
                    time_str = QtCore.QDateTime.fromMSecsSinceEpoch(val, time_spec).toString('MMM')
                elif time_str.endswith('00:00'):
                    time_str = QtCore.QDateTime.fromMSecsSinceEpoch(val, time_spec).toString('d')
                else:
                    time_str = QtCore.QDateTime.fromMSecsSinceEpoch(val, time_spec).toString('HH:mm')

                # skip this tick if it is too close to previous one
                if selected_timestamps and index - selected_timestamps[-1][1] < 3:
                    continue
                # we add increasing number of spaces to the timedate string as a workaround
                # for a stupid Qt requirement for category labels to be unique (no duplicates)
                # at least Qt seems to trim the trailing spaces when showing the labels
                num_ticks += 1
                selected_timestamps.append((time_str + ' ' * num_ticks, index))

            else:
                if time_str.endswith('01:00:00') and selected_timestamps[-1] != index:
                    time_str = QtCore.QDateTime.fromMSecsSinceEpoch(val, time_spec).toString('MMM')
                    # remove previous tick if it is too close to this one
                    if selected_timestamps and index - selected_timestamps[-1][1] < 4:
                        selected_timestamps.pop(-1)
                    num_ticks += 1
                    selected_timestamps.append((time_str + ' ' * num_ticks, index))

        return selected_timestamps


    def setCandleColors(self, candleSet: QtChart.QCandlestickSet):
        """Sets the candle colors (green and red)
        :param candleSet:  a QCandlestickSet set of candles
        """
        if candleSet.close() < candleSet.open():
            candleSet.setPen(QtGui.QPen(QtCore.Qt.red, 1))
            candleSet.setBrush(QtGui.QBrush(QtCore.Qt.red))
        else:
            candleSet.setPen(QtGui.QPen(QtCore.Qt.green, 1))
            candleSet.setBrush(QtGui.QBrush(QtCore.Qt.black))


    def clear(self):
        """Removes candlestick data"""
        if self.candlestickSeries.count() > 0:
            self.candlestickSeries.remove(self.candlestickSeries.sets())


    # ------------------------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------------------------

    def hoverMoveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):
        """Handles hover event by showing hover price line."""
        event.setAccepted(True)
        pos = self.mapToParent(event.pos())
        val = self.mapToValue(pos)
        self.hoverLine.clear()
        self.hoverLine.append(0, val.y())
        self.hoverLine.append(1, val.y())

        if val.y() > 0:
            precision = min(abs(int(math.log10(val.y())) - 4), 8)
        else:
            precision = 1

        # TODO calculate offsets instead of hard coding it
        self.hoverLinePriceTag.setPos(self.plotArea().getCoords()[2] + 5, pos.y() - 7)
        self.hoverLinePriceTag.setText('{:.{prec}f}'.format(val.y(), prec=min(precision, 8)))
        # self.hoverLinePriceTag.setText(f'{val.y():.{min(precision, 8)}f}')

        font = self.hoverLinePriceTag.font()
        font.setPointSize(8)
        self.hoverLinePriceTag.setFont(font)

        y_axes = self.hoverLine.attachedAxes()[0]
        if y_axes.min() < val.y() < y_axes.max():
            self.hoverLinePriceTag.show()
        else:
            self.hoverLinePriceTag.hide()

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):
        self.hoverLine.hide()
        self.hoverLinePriceTag.hide()

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):
        self.hoverLine.show()


